from django.urls import path
from .views import UploadImageAPIView
from .views import SymptomSearchAPIView

urlpatterns = [
    path('upload/', UploadImageAPIView.as_view(), name='upload-image'),
    path("ask/", SymptomSearchAPIView.as_view(), name="symptom-ask"),
]
