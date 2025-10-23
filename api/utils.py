import re

def normalize_query(q: str) -> str:
    q = re.sub(r"[^A-Za-z0-9\s]+", " ", q)
    q = re.sub(r"\s{2,}", " ", q).strip()
    return q

def query_for_url(q: str) -> str:
    return q.replace(" ", "+")