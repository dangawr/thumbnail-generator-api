from rest_framework import viewsets, mixins, views, status
from . import serializers
from .models import Image, TemporaryLinkModel
from .permissions import TempLinkUser
from rest_framework.response import Response
from datetime import datetime
from django.shortcuts import redirect


class ImageViewSet(mixins.ListModelMixin,
                   mixins.CreateModelMixin,
                   viewsets.GenericViewSet):

    queryset = Image.objects.all()
    serializer_class = serializers.ImageSerializer

    def get_queryset(self):
        return self.queryset.filter(user=self.request.user)

    def perform_create(self, serializer):
        return serializer.save(user=self.request.user)


class BinaryImage(mixins.RetrieveModelMixin,
                  viewsets.GenericViewSet):

    queryset = Image.objects.all()
    serializer_class = serializers.BinaryImageSerializer

    def get_queryset(self):
        return self.queryset.filter(user=self.request.user)


class TempLinkGenerate(views.APIView):
    permission_classes = [TempLinkUser]

    def get(self, request):
        return Response(None)

    def post(self, request):
        serializer = serializers.TemporaryLinkSerializer(data=request.data, context={'request': request, })
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class BinaryImageValidation(views.APIView):

    def get(self, request, access_code):
        temp_link_obj = TemporaryLinkModel.objects.get(one_time_code=access_code)
        expire_date = temp_link_obj.expiry_time
        if expire_date > datetime.now(expire_date.tzinfo):
            image = temp_link_obj.image
            return redirect('images:binary-detail', pk=image.pk)
        else:
            return Response({'error': 'No images found'})
