# api/views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.parsers import MultiPartParser, FormParser

from api.openai_helper import analyze_symptoms_to_keywords
from api.serializers import SymptomAIResultSerializer, SymptomQuerySerializer
from .ocr import extract_text_from_image
from .hf_nlp import keywords_from_text
from .scrapers import multi_search

def _normalize_query_from_keywords(keywords: list[str]) -> str:
    # join top tokens into a retailer-friendly query
    return "+".join([k.replace(" ", "+") for k in keywords[:4]]) or ""

class UploadImageAPIView(APIView):
    parser_classes = (MultiPartParser, FormParser)

    def post(self, request, *args, **kwargs):
        f = request.FILES.get("image")
        if not f:
            return Response({"detail": "Provide image in form-data with key 'image'."}, status=400)

        # 1) OCR
        text = extract_text_from_image(f)

        # 2) HF keywords
        kws = keywords_from_text(text)
        q = _normalize_query_from_keywords(kws) or "ibuprofen"

        # 3) Scrape
        retailers = request.GET.get("retailers", "walmart,target,costco").split(",")
        results = multi_search(q, retailers)

        return Response({
            "ocr_text": text,
            "keywords": kws,
            "query": q,
            "retailers": [r.strip().lower() for r in retailers],
            "results": results
        }, status=200)

class SearchProductsAPIView(APIView):
    def get(self, request):
        raw = request.GET.get("query", "").strip()
        if not raw:
            return Response({"detail": "query is required"}, status=400)

        kws = keywords_from_text(raw)
        q = _normalize_query_from_keywords(kws) or raw.replace(" ", "+")
        retailers = request.GET.get("retailers", "walmart,target,costco").split(",")
        results = multi_search(q, retailers)

        return Response({
            "keywords": kws,
            "query": q,
            "retailers": [r.strip().lower() for r in retailers],
            "results": results
        }, status=200)
    
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
