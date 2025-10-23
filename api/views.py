import os
from dotenv import load_dotenv

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.parsers import MultiPartParser, FormParser

from api.openai_helper import analyze_symptoms_to_keywords
from api.serializers import SymptomAIResultSerializer, SymptomQuerySerializer
from .ocr import extract_text_from_image

from .hf_nlp import keywords_from_text

from .providers_serpapi import google_shopping_search

# helpers to clean user query
from .utils import normalize_query
load_dotenv()

SEARCH_BACKEND = os.getenv("SEARCH_BACKEND", "serpapi")  # serpapi | scrape | both

class SearchProductsAPIView(APIView):
    """
    GET /api/search/?query=ibuprofen&retailers=walmart,target,cvs
    Plain text query; do NOT run NER here.
    """
    def get(self, request):
        raw = (request.GET.get("query") or "").strip()
        if not raw:
            return Response({"detail": "query is required"}, status=400)

        clean = normalize_query(raw)  # "ibuprofen 200mg"
        retailers = [r.strip().lower() for r in request.GET.get("retailers", "walmart,target").split(",") if r.strip()]

        # Use SerpAPI (stable). If you want Selenium later, add behind a flag.
        results = google_shopping_search(clean, retailers)

        return Response({
            "keywords": [],           # always [] for GET text search
            "query": clean,           # human-readable text (no "##" junk)
            "retailers": retailers,
            "results": results
        }, status=200)


class UploadImageAPIView(APIView):
    """
    POST /api/upload/  (form-data: image=<file>)
    Image → OCR → (optional NER to extract product words) → SerpAPI
    """
    parser_classes = (MultiPartParser, FormParser)

    def post(self, request, *args, **kwargs):
        f = request.FILES.get("image")
        if not f:
            return Response({"detail": "Provide image in form-data with key 'image'."}, status=400)

        ocr_text = extract_text_from_image(f) or ""
        kws = keywords_from_text(ocr_text)  # merge subwords in hf_nlp to avoid "##"
        # Prefer keywords if we got any; else fall back to normalized OCR text
        query_text = normalize_query(" ".join(kws) if kws else ocr_text) or "ibuprofen"

        retailers = [r.strip().lower() for r in request.GET.get("retailers", "walmart,target,cvs").split(",") if r.strip()]
        results = google_shopping_search(query_text, retailers)

        return Response({
            "ocr_text": ocr_text,
            "keywords": kws,
            "query": query_text,      # plain text for readability
            "retailers": retailers,
            "results": results
        }, status=200)


class SymptomSearchAPIView(APIView):
    """
    POST /api/ask/
    Body: { "query": "I have acne and oily skin, what should I look for?" }
    """
    def post(self, request, *args, **kwargs):
        input_ser = SymptomQuerySerializer(data=request.data)
        input_ser.is_valid(raise_exception=True)
        query = input_ser.validated_data["query"]

        ai_data = analyze_symptoms_to_keywords(query)
        output_ser = SymptomAIResultSerializer(ai_data)
        data = output_ser.data

        disclaimer = (
            "Not medical advice. For persistent or severe symptoms, consult a licensed healthcare professional."
        )
        return Response({"data": data, "disclaimer": disclaimer}, status=status.HTTP_200_OK)
