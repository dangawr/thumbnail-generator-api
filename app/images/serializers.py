from rest_framework import serializers
from .models import Image, TemporaryLinkModel
from easy_thumbnails.files import get_thumbnailer
import base64
from datetime import datetime, timedelta
import random
import string


def randomstring(stringlength=20):
    """Generate a random string of fixed length """
    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for i in range(stringlength))


class ImageSerializer(serializers.ModelSerializer):
    thumbnails = serializers.SerializerMethodField()

    class Meta:
        model = Image
        fields = ['id', 'original_image', 'thumbnails']
        read_only_fields = ('id',)

    def get_thumbnails(self, obj):
        request = self.context['request']
        user_tier_sizes = [str(size.size_px) for size in request.user.tier.sizes.all()]  # List of user's tier sizes
        thumbnailer = get_thumbnailer(obj.original_image)
        thumbnails_response = {}
        for size in user_tier_sizes:
            thumbnails_response[size] =\
                request.build_absolute_uri(thumbnailer.get_thumbnail({'size': (0, int(size))}).url)
        return thumbnails_response

    # def get_fields(self):
    #     fields = super().get_fields()
    #     if not self.context['request'].user.tier.original:
    #         fields.pop('original_image')
    #     return fields


class BinaryImageSerializer(serializers.ModelSerializer):
    binary_image = serializers.SerializerMethodField()

    class Meta:
        model = Image
        fields = ['binary_image', ]

    def get_binary_image(self, obj):
        return base64.b64encode(obj.original_image.read())


class TemporaryLinkSerializer(serializers.ModelSerializer):
    seconds_to_expire = serializers.IntegerField(write_only=True)
    image_id = serializers.IntegerField(write_only=True)
    temp_link = serializers.SerializerMethodField()

    class Meta:
        model = TemporaryLinkModel
        fields = ['seconds_to_expire', 'image_id', 'temp_link']

    def create(self, validated_data):
        seconds = validated_data.pop('seconds_to_expire')
        image_id = validated_data.pop('image_id')
        expiring_date = datetime.now() + timedelta(seconds=seconds)
        the_string = randomstring(stringlength=20)
        image = Image.objects.get(pk=image_id)
        temp_link = TemporaryLinkModel.objects.create(expiry_time=expiring_date, one_time_code=the_string, image=image)
        return temp_link

    def get_temp_link(self, obj):
        the_string = obj.one_time_code
        return self.context['request'].build_absolute_uri(f'/images/binary/{the_string}')


