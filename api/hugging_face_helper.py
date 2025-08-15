from transformers import pipeline
from django.conf import settings

# small, fast sentiment to route: sleep vs pain vs acne vs hair (toy example)
_nlp = pipeline("sentiment-analysis", model=settings.HF_MODEL)

SYMPTOM_KB = {
    "sleep": (["insomnia","sleep","awake","melatonin","gummies"], ["melatonin","valerian","sleep gummies"]),
    "pain":  (["pain","ache","headache","back"], ["ibuprofen","acetaminophen","naproxen"]),
    "acne":  (["acne","pimple","zit","oily"], ["benzoyl peroxide","salicylic acid","adapalene"]),
    "hair":  (["hair","fall","loss","itchy scalp"], ["minoxidil","biotin","ketoconazole shampoo"]),
}

def hf_keywords(query: str):
    q = query.lower()
    cats = []
    kws = []
    for cat, (trigs, picks) in SYMPTOM_KB.items():
        if any(t in q for t in trigs):
            cats.append(cat)
            kws.extend(picks)
    # sentiment is optional here—example how to use HF locally
    _ = _nlp(query)  # warm-up / potential routing signal
    return {
        "cleaned_symptoms": [],
        "candidate_keywords": sorted(set(kws)),
        "categories": sorted(set(cats)),
        "safety_flags": ["hf_local_used"] if kws else []
    }
