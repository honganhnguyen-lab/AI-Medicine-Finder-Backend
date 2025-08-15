from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.parsers import MultiPartParser, FormParser
from .serializers import UploadedImageSerializer
from .serializers import SymptomQuerySerializer, SymptomAIResultSerializer
from .hugging_face_helper import hf_keywords
from .openai_helper import analyze_symptoms_to_keywords
import logging

logger = logging.getLogger(__name__)

class UploadImageAPIView(APIView):
    parser_classes = (MultiPartParser, FormParser)

    def post(self, request, *args, **kwargs):
        print("DEBUG: request =", request)
        print("DEBUG: request.data =", request.data)
        logger.debug(f"request: {request}")
        logger.debug(f"request.data: {list(request.data)}")
        file_obj = request.data.get('image')

        print("DEBUG: file_obj =", file_obj)
        logger.debug(f"file_obj: {file_obj}")
        
        if not file_obj:
            return Response(
                {"detail": "No file under key 'image'."},
                status=status.HTTP_400_BAD_REQUEST
            )

        serializer = UploadedImageSerializer(data={'image': file_obj})
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"message": "Image uploaded", "data": serializer.data},
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

class SymptomSearchAPIView(APIView):
    """
    POST /api/ask/
    Body: { "query": "I have acne and oily skin, what should I look for?" }
    Returns structured JSON with search keywords.
    """
    def post(self, request, *args, **kwargs):
        input_ser = SymptomQuerySerializer(data=request.data)
        input_ser.is_valid(raise_exception=True)
        query = input_ser.validated_data["query"]

        ai_data = analyze_symptoms_to_keywords(query)
        output_ser = SymptomAIResultSerializer(ai_data)
        data = output_ser.data

        ## required disclaimer
        disclaimer = (
            "Not medical advice. For persistent or severe symptoms, consult a licensed healthcare professional."
        )
        return Response({"data": data, "disclaimer": disclaimer}, status=status.HTTP_200_OK)
    
    class SymptomSearchHFAPIView(APIView):
        def post(self, request):
            ser = SymptomQuerySerializer(data=request.data); ser.is_valid(raise_exception=True)
            data = hf_keywords(ser.validated_data["query"])
            out = SymptomAIResultSerializer(data); return Response({"data": out.data}, status=200)


