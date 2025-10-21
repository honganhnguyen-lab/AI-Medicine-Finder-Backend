# api/scrapers.py
from __future__ import annotations
from typing import List, Dict
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def _make_driver(headless: bool = True):
    opts = Options()
    if headless:
        opts.add_argument("--headless=new")
    opts.add_argument("--no-sandbox")
    opts.add_argument("--disable-dev-shm-usage")
    opts.add_argument("--disable-gpu")
    opts.add_argument("--window-size=1280,1024")
    opts.add_argument("--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116 Safari/537.36")
    return webdriver.Chrome(options=opts)

def _page_soup(driver, css: str, timeout: int = 12):
    WebDriverWait(driver, timeout).until(EC.presence_of_element_located((By.CSS_SELECTOR, css)))
    return BeautifulSoup(driver.page_source, "lxml")

# walmart
def search_walmart(query: str) -> List[Dict]:
    url = f"https://www.walmart.com/search?q={query}"
    d = _make_driver()
    try:
        d.get(url)
        soup = _page_soup(d, 'div[data-automation-id="products-list"]')
        items = []
        for card in soup.select('div[data-automation-id="product"]')[:10]:
            a = card.select_one("a[aria-label]")
            link = card.select_one("a[href]")
            title = a.get("aria-label") if a else None
            href = f"https://www.walmart.com{link['href']}" if link and link.get("href","").startswith("/") else (link["href"] if link else None)
            price_el = card.select_one("[data-automation-id='product-price']")
            price = price_el.get_text(strip=True) if price_el else None
            if title and href:
                items.append({"retailer":"walmart","title":title,"price":price,"url":href})
        return items
    finally:
        d.quit()

# target
def search_target(query: str) -> List[Dict]:
    url = f"https://www.target.com/s?searchTerm={query}"
    d = _make_driver()
    try:
        d.get(url)
        soup = _page_soup(d, "div[data-test=results-list]")
        items = []
        for a in soup.select("a[data-test=product-title]")[:10]:
            title = a.get_text(strip=True)
            href = "https://www.target.com" + a.get("href","")
            price_node = a.find_parent().select_one("[data-test=current-price]")
            price = price_node.get_text(strip=True) if price_node else None
            items.append({"retailer":"target","title":title,"price":price,"url":href})
        return items
    finally:
        d.quit()

# costco
def search_costco(query: str) -> List[Dict]:
    url = f"https://www.costco.com/CatalogSearch?dept=All&keyword={query}"
    d = _make_driver()
    try:
        d.get(url)
        soup = _page_soup(d, "div.product-list")
        items = []
        for card in soup.select("div.product-tile-set")[:10]:
            a = card.select_one("a[href]")
            title = a.get_text(strip=True) if a else None
            href = ("https://www.costco.com" + a["href"]) if a and a["href"].startswith("/") else (a["href"] if a else None)
            price_el = card.select_one(".price")
            price = price_el.get_text(strip=True) if price_el else None
            if title and href:
                items.append({"retailer":"costco","title":title,"price":price,"url":href})
        return items
    finally:
        d.quit()

# amazon
def search_amazon(query: str) -> List[Dict]:
    url = f"https://www.amazon.com/s?k={query}"
    d = _make_driver()
    try:
        d.get(url)
        soup = _page_soup(d, "div.s-main-slot")
        items = []
        for card in soup.select("div.s-result-item")[:10]:
            t = card.select_one("h2 a")
            if not t:
                continue
            title = t.get_text(strip=True)
            href = "https://www.amazon.com" + t["href"]
            price = None
            money = card.select_one("span.a-price > span.a-offscreen")
            if money: price = money.get_text(strip=True)
            items.append({"retailer":"amazon","title":title,"price":price,"url":href})
        return items
    finally:
        d.quit()

# cvs
def search_cvs(query: str) -> List[Dict]:
    url = f"https://www.cvs.com/search/?filterBy=all&query={query}"
    d = _make_driver()
    try:
        d.get(url)
        soup = _page_soup(d, "div[data-testid='product-grid'], main")
        items: List[Dict] = []
        for card in soup.select("a[data-testid='product-card-name'], a[href*='/shop/']")[:12]:
            title = card.get_text(strip=True)
            href = card.get("href", "")
            if not href:
                continue
            if href.startswith("/"):
                href = "https://www.cvs.com" + href
            price_el = card.find_parent().select_one("[data-testid='product-price'], .css-1i6m1b8, .price__value")
            price = price_el.get_text(strip=True) if price_el else None
            if title and href:
                items.append({"retailer":"cvs","title":title,"price":price,"url":href})
        return items[:10]
    finally:
        d.quit()

# walgreen
def search_walgreens(query: str) -> List[Dict]:
    url = f"https://www.walgreens.com/search/results.jsp?Ntt={query}"
    d = _make_driver()
    try:
        d.get(url)
        soup = _page_soup(d, "div#wag-return")
        items: List[Dict] = []
        for card in soup.select("div.product__container")[:12]:
            a = card.select_one("a.product__title, a[aria-label][href]")
            if not a:
                a = card.select_one("a[href*='/store/']")
            if not a:
                continue
            title = a.get_text(strip=True) or a.get("aria-label", "").strip()
            href = a.get("href", "")
            if href.startswith("/"):
                href = "https://www.walgreens.com" + href
            price_el = card.select_one(".product__price__final, .product__price, [data-qa='product-price'], .price")
            price = price_el.get_text(strip=True) if price_el else None
            if title and href:
                items.append({"retailer":"walgreens","title":title,"price":price,"url":href})
        return items[:10]
    finally:
        d.quit()


PRIORITY = ["cvs", "walmart", "target", "costco", "amazon", "walgreens"]

def multi_search(query: str, retailers: List[str]) -> List[Dict]:
    """
    Run scrapers for requested retailers, honoring PRIORITY order.
    """
    wanted = [r.strip().lower() for r in retailers if r.strip()]
    wanted = sorted(set(wanted), key=lambda r: (PRIORITY.index(r) if r in PRIORITY else 999, r))

    out: List[Dict] = []
    for r in wanted:
        try:
            if r == "cvs":
                out += search_cvs(query)
            elif r == "walmart":
                out += search_walmart(query)
            elif r == "target":
                out += search_target(query)
            elif r == "costco":
                out += search_costco(query)
            elif r == "amazon":
                out += search_amazon(query)
            elif r == "walgreens":
                out += search_walgreens(query)
            else:
                out.append({"retailer": r, "error": "unsupported retailer"})
        except Exception as e:
            out.append({"retailer": r, "error": str(e)})
    return out[:40]
