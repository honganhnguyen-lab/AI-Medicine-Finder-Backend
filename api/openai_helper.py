# api/openai_helper.py
import json, time, logging
from typing import Dict, Any, List
from openai import OpenAI, APIConnectionError, RateLimitError, BadRequestError, AuthenticationError
from django.conf import settings

log = logging.getLogger(__name__)
client = OpenAI(api_key=settings.OPENAI_API_KEY)

SYSTEM = """
You are a pharmacy query normalizer. Given a user's free-text symptoms, return JSON:
{"cleaned_symptoms":[...],"candidate_keywords":[...],"categories":[...],"safety_flags":[...]}
Return ONLY minified JSON (no prose).
"""

def _messages(user_query: str) -> List[Dict[str, str]]:
    return [
        {"role": "system", "content": SYSTEM},
        {"role": "user", "content": user_query.strip()}
    ]

def _fallback_keywords(q: str) -> Dict[str, Any]:
    ql = q.lower()
    kw = []
    cats = []
    if any(w in ql for w in ["sleep", "insomnia", "melatonin", "awake"]):
        kw += ["melatonin", "sleep gummies", "valerian"]
        cats += ["sleep"]
    if any(w in ql for w in ["stomach", "gas", "relief", "diarrhea"]):
        kw += ["rolaids", "maalox", "mylanta"]
        cats += ["stomachache"]
    if any(w in ql for w in ["pain", "headache", "sore", "ache"]):
        kw += ["ibuprofen", "acetaminophen", "naproxen"]
        cats += ["pain relief"]
    if any(w in ql for w in ["acne", "pimple"]):
        kw += ["benzoyl peroxide", "salicylic acid", "adapalene"]
        cats += ["acne"]
    if any(w in ql for w in ["hair", "fall", "loss"]):
        kw += ["biotin", "minoxidil", "ketoconazole shampoo"]
        cats += ["hair care"]
    return {
        "cleaned_symptoms": [],
        "candidate_keywords": list(dict.fromkeys(kw)),
        "categories": list(dict.fromkeys(cats)),
        "safety_flags": ["fallback_used"]
    }

def analyze_symptoms_to_keywords(user_query: str, retries: int = 3, backoff: float = 1.25) -> Dict[str, Any]:
    if not settings.OPENAI_API_KEY:
        return _fallback_keywords(user_query)

    msgs = _messages(user_query)
    for attempt in range(retries + 1):
        try:
            resp = client.chat.completions.create(
                model=getattr(settings, "OPENAI_MODEL", "gpt-4o-mini"),
                messages=msgs,
                temperature=0.1,
                max_tokens=200,
                response_format={"type": "json_object"},
                timeout=getattr(settings, "OPENAI_TIMEOUT", 20),
            )
            raw = resp.choices[0].message.content
            data = json.loads(raw)
            for k in ["cleaned_symptoms", "candidate_keywords", "categories", "safety_flags"]:
                data.setdefault(k, [])
            return data
        except RateLimitError as e:
            log.warning("OpenAI rate limit: %s", e)
            if attempt < retries:
                time.sleep(backoff ** attempt)
                continue
            # final fallback
            fb = _fallback_keywords(user_query)
            fb["safety_flags"].append("openai_rate_limited")
            return fb
        except (APIConnectionError, BadRequestError, AuthenticationError, Exception) as e:
            log.error("OpenAI error: %s", e)
            # deterministic fallback so UI keeps working
            fb = _fallback_keywords(user_query)
            fb["safety_flags"].append(f"openai_error:{type(e).__name__}")
            return fb
