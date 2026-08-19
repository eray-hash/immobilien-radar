from __future__ import annotations

import re

from bs4 import BeautifulSoup

from . import config
from .http_client import get

_PRICE_RE = re.compile(r"([\d.]+)\s*€")
_M2_RE = re.compile(r"([\d.,]+)\s*m²")
_PLZ_ORT_RE = re.compile(r"(\d{5})\s+(.+)")
_YEAR_RE = re.compile(r"\b(1[89]\d{2}|20\d{2})\b")


def _search_url(keyword: str, page: int) -> str:
    slug = keyword.replace(" ", "-")
    if page <= 1:
        return f"{config.BASE_URL}/s-haus-kaufen/{slug}/k0c{config.CATEGORY_ID}"
    return f"{config.BASE_URL}/s-haus-kaufen/seite:{page}/{slug}/k0c{config.CATEGORY_ID}"


def _parse_price(text: str) -> float | None:
    m = _PRICE_RE.search(text.replace("\xa0", " "))
    if not m:
        return None
    return float(m.group(1).replace(".", ""))


def _parse_m2(text: str) -> float | None:
    m = _M2_RE.search(text)
    if not m:
        return None
    return float(m.group(1).replace(".", "").replace(",", "."))


def parse_search_results(html: str) -> list[dict]:
    soup = BeautifulSoup(html, "lxml")
    results = []
    for article in soup.select("article.aditem"):
        adid = article.get("data-adid")
        href = article.get("data-href")
        if not adid or not href:
            continue

        title_el = article.select_one("h2 a.ellipsis")
        title = title_el.get_text(strip=True) if title_el else None

        loc_el = article.select_one(".aditem-main--top--left")
        loc_text = loc_el.get_text(strip=True) if loc_el else ""
        plz, ort = None, None
        m = _PLZ_ORT_RE.search(loc_text)
        if m:
            plz, ort = m.group(1), m.group(2)

        tags_el = article.select_one(".aditem-main--middle--tags")
        wohnflaeche = _parse_m2(tags_el.get_text(" ", strip=True)) if tags_el else None

        price_el = article.select_one(".aditem-main--middle--price-shipping--price")
        preis = _parse_price(price_el.get_text(" ", strip=True)) if price_el else None

        bottom_el = article.select_one(".aditem-main--bottom")
        bottom_text = bottom_el.get_text(" ", strip=True) if bottom_el else ""
        anbieter_typ = "privat" if "Von Privat" in bottom_text else "gewerblich"

        is_top = article.select_one(".aditem-image--badges--badge-topad") is not None

        results.append(
            {
                "id": adid,
                "url": config.BASE_URL + href,
                "title": title,
                "plz": plz,
                "ort": ort,
                "wohnflaeche_m2": wohnflaeche,
                "preis_eur": preis,
                "anbieter_typ": anbieter_typ,
                "top_anzeige": is_top,
            }
        )
    return results


def parse_detail(html: str) -> dict:
    soup = BeautifulSoup(html, "lxml")
    detail = {}

    for li in soup.select(".addetailslist--detail"):
        value_el = li.select_one(".addetailslist--detail--value")
        if not value_el:
            continue
        label = li.get_text(" ", strip=True).replace(value_el.get_text(strip=True), "").strip()
        value = value_el.get_text(strip=True)
        key = label.lower()
        if "wohnfläche" in key:
            detail["wohnflaeche_m2"] = _parse_m2(value + " m²") if "m²" not in value else _parse_m2(value)
        elif "baujahr" in key:
            m = _YEAR_RE.search(value)
            detail["baujahr"] = int(m.group(1)) if m else None
        elif "etagen" in key:
            detail["etagen"] = value
        elif "grundstücksfläche" in key:
            detail["grundstuecksflaeche_m2"] = _parse_m2(value + " m²") if "m²" not in value else _parse_m2(value)
        elif "zimmer" in key:
            detail["zimmer"] = value

    locality_el = soup.select_one("#viewad-locality")
    if locality_el:
        text = locality_el.get_text(strip=True)
        m = re.match(r"(\d{5})\s+(.+?)\s*-\s*(.+)", text)
        if m:
            detail["plz"] = m.group(1)
            detail["bundesland"] = m.group(2)
            detail["ort"] = m.group(3)

    price_el = soup.select_one("#viewad-price")
    if price_el:
        detail["preis_eur"] = _parse_price(price_el.get_text(" ", strip=True))

    desc_el = soup.select_one("#viewad-description-text")
    if desc_el:
        detail["beschreibung"] = desc_el.get_text("\n", strip=True)

    if detail.get("baujahr") is None and desc_el:
        m = re.search(r"[Bb]aujahr[:\s]*?(\d{4})", desc_el.get_text(" ", strip=True))
        if m:
            detail["baujahr"] = int(m.group(1))

    return detail


def _fetch_page_with_retry(url: str, retries: int = 2) -> list[dict]:
    # kleinanzeigen liefert bei "Empfohlen"-Sortierung gelegentlich eine leere
    # Trefferliste im selben HTML-Gerüst zurück (transientes Server-/CDN-Verhalten,
    # kein robots.txt- oder Statuscode-Fehler) - daher hier mit erneutem Versuch abfedern.
    for attempt in range(retries + 1):
        html = get(url)
        if html is None:
            return []
        results = parse_search_results(html)
        if results:
            return results
        if attempt < retries:
            print(f"  0 Treffer bei {url} (Versuch {attempt + 1}/{retries + 1}), erneuter Versuch...")
    return []


def fetch_search_results(keyword: str) -> list[dict]:
    all_results = []
    for page in range(1, config.MAX_PAGES_PER_SEARCH + 1):
        page_results = _fetch_page_with_retry(_search_url(keyword, page))
        if not page_results:
            break
        all_results.extend(page_results)
        if len(page_results) < 25:
            break  # letzte Seite erreicht
    return all_results


def fetch_detail(url: str) -> dict:
    html = get(url)
    if html is None:
        return {}
    return parse_detail(html)
