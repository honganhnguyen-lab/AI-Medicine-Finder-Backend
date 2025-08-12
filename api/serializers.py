from rest_framework import serializers
from .models import UploadedImage

class UploadedImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = UploadedImage
        fields = ['id', 'image', 'uploaded_at']

class SymptomQuerySerializer(serializers.Serializer):
    query = serializers.CharField(max_length=1000)

class SymptomAIResultSerializer(serializers.Serializer):
    cleaned_symptoms = serializers.ListField(child=serializers.CharField(), required=False)
    candidate_keywords = serializers.ListField(child=serializers.CharField(), required=False)
    categories = serializers.ListField(child=serializers.CharField(), required=False)
    safety_flags = serializers.ListField(child=serializers.CharField(), required=False)

