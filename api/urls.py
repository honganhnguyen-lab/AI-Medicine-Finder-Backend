from django.urls import path
from .views import UploadImageAPIView

urlpatterns = [
    path('upload/', UploadImageAPIView.as_view(), name='upload-image'),
]
