from rest_framework import viewsets, mixins, views, status
from . import serializers
from .models import Image, TemporaryLinkModel
from .permissions import TempLinkUser
from rest_framework.response import Response
from datetime import datetime
from rest_framework.permissions import IsAuthenticated


class ImageViewSet(mixins.ListModelMixin,
                   mixins.CreateModelMixin,
                   viewsets.GenericViewSet):

    queryset = Image.objects.all()
    serializer_class = serializers.ImageSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return self.queryset.filter(user=self.request.user)

    def perform_create(self, serializer):
        return serializer.save(user=self.request.user)


class TempLinkGenerate(views.APIView):
    permission_classes = [IsAuthenticated, TempLinkUser]

    def get(self, request):
        return Response('Please use post method to create temporary link')

    def post(self, request):
        serializer = serializers.TemporaryLinkSerializer(data=request.data, context={'request': request, })
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class BinaryImage(views.APIView):

    def get(self, request, access_code):
        try:
            temp_link_obj = TemporaryLinkModel.objects.get(one_time_code=access_code)
        except TemporaryLinkModel.DoesNotExist:
            return Response({'error': 'No images found'}, status=status.HTTP_404_NOT_FOUND)
        serializer = serializers.BinaryImageSerializer(temp_link_obj, context={'request': request, })
        return Response(serializer.data)
