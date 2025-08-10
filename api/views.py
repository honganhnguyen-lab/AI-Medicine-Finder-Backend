from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.parsers import MultiPartParser, FormParser
from .serializers import UploadedImageSerializer
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

