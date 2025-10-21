# api/hf_nlp.py
from transformers import pipeline
from django.conf import settings

_pipe = None
_ner = None

def _get_cls():
    global _pipe
    if _pipe is None:
        model = getattr(settings, "HF_MODEL", "distilbert-base-uncased-finetuned-sst-2-english")
        _pipe = pipeline("text-classification", model=model)
    return _pipe

def _get_ner():
    global _ner
    # generic NER; replace with a biomedical NER model later if you like
    _ner = _ner or pipeline("token-classification", model="dslim/bert-base-NER", aggregation_strategy="simple")
    return _ner

def keywords_from_text(text: str) -> list[str]:
    """
    Very simple keywording via NER. Later you can switch to a biomedical NER.
    """
    text = (text or "").strip()
    if not text:
        return []
    ents = _get_ner()(text)  # [{'entity_group':'ORG','word':'...','score':...}, ...]
    tokens = [e["word"] for e in ents if e["entity_group"] in {"ORG", "PRODUCT", "MISC", "PER"}]
    # Add a crude fallback: return top words if NER is empty
    if not tokens:
        words = [w.strip(",.()").lower() for w in text.split() if len(w) > 3]
        tokens = list(dict.fromkeys(words))[:5]
    return tokens[:8]
