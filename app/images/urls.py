from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

app_name = 'images'

router = DefaultRouter()

router.register('', views.ImageViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('get-temp-link/', views.TempLinkGenerate.as_view(), name='get-temp-link'),
    path('binary/<str:access_code>', views.BinaryImageValidation.as_view(), name='binary-validation')
]
