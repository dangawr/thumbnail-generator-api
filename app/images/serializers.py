from rest_framework import serializers
from .models import Image, TemporaryLinkModel, Tier
from easy_thumbnails.files import get_thumbnailer
import random
import string
from django.utils import timezone
from django.core.exceptions import ObjectDoesNotExist


def randomstring(stringlength=20):
    """Generate a random string of fixed length for temporary link generation."""
    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for i in range(stringlength))


class ImageSerializer(serializers.ModelSerializer):
    thumbnails = serializers.SerializerMethodField()

    class Meta:
        model = Image
        fields = ['id', 'original_image', 'thumbnails']
        extra_kwargs = {'original_image': {'write_only': True}, 'id': {'read_only': True}}

    def get_thumbnails(self, obj):
        """
        Generating thumbnails based on user's tier sizes.
        """
        request = self.context['request']
        if not request.user.tier:
            request.user.tier = Tier.objects.get(name='Basic')
        user_tier_sizes = [str(size.size_px) for size in request.user.tier.sizes.all()]  # List of user's tier sizes
        thumbnailer = get_thumbnailer(obj.original_image)
        thumbnails_response = {}
        for size in user_tier_sizes:
            thumbnails_response[size] =\
                request.build_absolute_uri(thumbnailer.get_thumbnail({'size': (0, int(size))}).url)
        return thumbnails_response

    def get_extra_kwargs(self):
        """
        Check if user's tier have original image display.
        """
        extra_kwargs = super().get_extra_kwargs()
        if self.context['request'].user.tier.original:
            extra_kwargs.pop('original_image')
        return extra_kwargs


class TemporaryLinkSerializer(serializers.ModelSerializer):
    seconds_to_expire = serializers.IntegerField(write_only=True)
    image_id = serializers.IntegerField(write_only=True)
    temp_link = serializers.SerializerMethodField()

    class Meta:
        model = TemporaryLinkModel
        fields = ['seconds_to_expire', 'image_id', 'temp_link']

    def validate(self, attrs):
        """
        Validates request data.
        """
        if 300 <= attrs['seconds_to_expire'] <= 30000:
            return attrs
        else:
            raise serializers.ValidationError({
                'seconds_to_expire': 'Sorry, specify seconds between 300 and 30000.'
            })

    def create(self, validated_data):
        """
        Creates temporary link.
        """
        seconds = validated_data.pop('seconds_to_expire')
        image_id = validated_data.pop('image_id')
        expiring_date = timezone.now() + timezone.timedelta(seconds=seconds)
        the_string = randomstring(stringlength=20)
        try:
            image = Image.objects.get(pk=image_id)
        except ObjectDoesNotExist:
            raise serializers.ValidationError({'image_id': 'Image does not exists'})
        if image.user == self.context['request'].user:
            temp_link = TemporaryLinkModel.objects.create(
                expiry_time=expiring_date,
                one_time_code=the_string,
                image=image
            )
            return temp_link
        else:
            raise serializers.ValidationError({'image_id': 'Image id is not correct'})

    def get_temp_link(self, obj):
        """
        Method field for temporary link display.
        """
        the_string = obj.one_time_code
        return self.context['request'].build_absolute_uri(f'/images/binary/{the_string}')


