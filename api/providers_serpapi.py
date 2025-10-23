# api/providers_serpapi.py
import os, requests
from urllib.parse import urlparse

SERPAPI_KEY = os.getenv("SERPAPI_KEY")
GL = os.getenv("SERPAPI_GL", "us")
HL = os.getenv("SERPAPI_HL", "en")
LOCATION = os.getenv("SERPAPI_LOCATION", "United States")

_ALLOWED = {
    "walmart":   ["walmart.com"],
    "target":    ["target.com"],
    "cvs":       ["cvs.com"],
    "walgreens": ["walgreens.com"],
    "costco":    ["costco.com"],
    "amazon":    ["amazon.com"],
}

def _host_ok(hostname: str, want: list[str]) -> bool:
    host = (hostname or "").lower().replace("www.", "")
    # collapse all allowed domains for requested retailers
    allowed = []
    for w in want:
        allowed += _ALLOWED.get(w, [])
    # accept exact end or obvious contain (some results include subpaths/cdn)
    return any(host.endswith(dom) or dom in host for dom in allowed)

def _map_item(link: str, title: str | None, price) -> dict:
    from_host = (urlparse(link).hostname or "").replace("www.", "")
    retailer = from_host
    for k, doms in _ALLOWED.items():
        if any(from_host.endswith(d) for d in doms):
            retailer = k
            break
    return {
        "retailer": retailer,
        "title": (title or "").strip(),
        "price": str(price) if price not in (None, "") else None,
        "url": link,
    }

def _serpapi_get(params: dict):
    params = {
        **params,
        "gl": GL,
        "hl": HL,
        "location": LOCATION,
        "api_key": SERPAPI_KEY,
    }
    r = requests.get("https://serpapi.com/search.json", params=params, timeout=25)
    r.raise_for_status()
    return r.json()

def google_shopping_search(query: str, retailers: list[str], num: int = 24, debug: bool = False):
    if not SERPAPI_KEY:
        return [{"retailer":"serpapi", "error":"SERPAPI_KEY missing"}]

    out = []

    # --- Pass 1: Google Shopping engine ---
    try:
        data = _serpapi_get({
            "engine": "google_shopping",
            "q": query,
            "num": str(num),
        })
    except Exception as e:
        data = {}
        if debug: out.append({"retailer":"serpapi","error":f"shopping engine error: {e}"})

    candidates = []
    for key in ("shopping_results", "product_results", "organic_results"):
        items = data.get(key) or []
        if items:
            candidates.extend(items)

    # Map + filter by domain
    for it in candidates:
        link  = it.get("link") or it.get("product_link") or it.get("source") or ""
        title = it.get("title") or it.get("product_title")
        price = it.get("price") or it.get("extracted_price")
        if not link:
            continue
        host = urlparse(link).hostname or ""
        if _host_ok(host, retailers):
            out.append(_map_item(link, title, price))
        if len(out) >= num:
            break

    if out:
        return out

    # --- Pass 2 (fallback): Google Web engine with site: filters ---
    # Build "site:walmart.com OR site:target.com ..." query
    site_parts = []
    for r in retailers:
        for dom in _ALLOWED.get(r, []):
            site_parts.append(f"site:{dom}")
    sites_query = " OR ".join(site_parts) if site_parts else ""
    web_q = f"{query} {sites_query}".strip()

    try:
        web = _serpapi_get({
            "engine": "google",
            "q": web_q,
            "num": str(num * 2),  # ask for more since we filter client-side
            "safe": "active",
        })
    except Exception as e:
        if debug:
            return [{"retailer":"serpapi","error":f"web engine error: {e}"}]
        return []

    for it in web.get("organic_results", []):
        link = it.get("link")
        title = it.get("title")
        if not link:
            continue
        host = urlparse(link).hostname or ""
        if _host_ok(host, retailers):
            out.append(_map_item(link, title, None))
        if len(out) >= num:
            break

    if debug and not out:
        # Help you see what we got back
        return [{
            "retailer":"serpapi",
            "debug": {
                "shopping_counts": {
                    "shopping_results": len(data.get("shopping_results") or []),
                    "product_results": len(data.get("product_results") or []),
                    "organic_results": len(data.get("organic_results") or []),
                },
                "web_query": web_q,
                "web_count": len(web.get("organic_results", [])) if isinstance(web, dict) else 0,
            }
        }]

    return out
