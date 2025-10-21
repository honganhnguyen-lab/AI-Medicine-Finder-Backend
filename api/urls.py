from django.urls import path
from .views import SearchProductsAPIView, UploadImageAPIView
from .views import SymptomSearchAPIView
from .views import SymptomAIResultSerializer

urlpatterns = [
    path('upload/', UploadImageAPIView.as_view(), name='upload-image'),
    path("ask/", SymptomSearchAPIView.as_view(), name="symptom-ask"),
    path("search/", SearchProductsAPIView.as_view(), name="search-products"),
    # path("ask_local/", SymptomSearchHFAPIView.as_view(), name="symptom-ask-hf"),

]
