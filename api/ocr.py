# api/ocr.py
from google.cloud import vision
from google.cloud.vision_v1.types import Image
from django.core.files.uploadedfile import UploadedFile

_client = None

def _get_client():
    global _client
    if _client is None:
        _client = vision.ImageAnnotatorClient()
    return _client

def extract_text_from_image(file: UploadedFile) -> str:
    content = file.read()
    image = Image(content=content)
    resp = _get_client().text_detection(image=image)
    if resp.error.message:
        raise RuntimeError(resp.error.message)
    annotations = resp.text_annotations
    if not annotations:
        return ""
    return annotations[0].description.strip()
