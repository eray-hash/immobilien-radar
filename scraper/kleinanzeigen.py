from __future__ import annotations

import re

from bs4 import BeautifulSoup

from . import config
from .http_client import get

# Deutsche Zahlformat-Dezimalstellen (",08") erlauben, sonst matcht bei
# "2.604,08 €/m²" nur das Fragment "08" vor dem €-Zeichen. "€/m²"-Angaben
# (Preis PRO Quadratmeter statt Gesamtpreis) explizit ausschliessen, sonst
# wird ein €/m²-Wert faelschlich als Gesamtpreis uebernommen.
_PRICE_RE = re.compile(r"([\d.]+(?:,\d+)?)\s*€(?!\s*/\s*m)")
_M2_RE = re.compile(r"([\d.,]+)\s*m²")
_PLZ_ORT_RE = re.compile(r"(\d{5})\s+(.+)")
_YEAR_RE = re.compile(r"\b(1[89]\d{2}|20\d{2})\b")

# Längere/zusammengesetzte Namen zuerst, damit z.B. "Sachsen-Anhalt" nicht als
# Teiltreffer von "Sachsen" verloren geht.
_BUNDESLAENDER = [
    "Baden-Württemberg",
    "Mecklenburg-Vorpommern",
    "Nordrhein-Westfalen",
    "Rheinland-Pfalz",
    "Sachsen-Anhalt",
    "Schleswig-Holstein",
    "Bayern",
    "Berlin",
    "Brandenburg",
    "Bremen",
    "Hamburg",
    "Hessen",
    "Niedersachsen",
    "Saarland",
    "Sachsen",
    "Thüringen",
]


def _page_url(path: str, page: int) -> str:
    # kleinanzeigen nutzt zwei URL-Formen, per Browser für jede Suche verifiziert:
    # - "k0c..."/"c..." ohne "+": seite: kommt direkt nach dem ersten Segment
    #   (z.B. s-haus-kaufen/seite:2/mehrfamilienhaus/k0c208)
    # - "c...+filter...": seite: kommt direkt vor dem letzten (Filter-)Segment
    #   (z.B. s-gewerbeimmobilien/kaufen/seite:2/c277+gewerbeimmobilien.art_s:kaufen)
    if page <= 1:
        return f"{config.BASE_URL}/{path}"
    segments = path.split("/")
    if "+" in segments[-1]:
        segments = segments[:-1] + [f"seite:{page}", segments[-1]]
    else:
        segments = [segments[0], f"seite:{page}", *segments[1:]]
    return f"{config.BASE_URL}/" + "/".join(segments)


def _parse_price(text: str) -> float | None:
    m = _PRICE_RE.search(text.replace("\xa0", " "))
    if not m:
        return None
    raw = m.group(1).replace(".", "").replace(",", ".")
    try:
        return float(raw)
    except ValueError:
        return None


def _parse_m2(text: str) -> float | None:
    m = _M2_RE.search(text)
    if not m:
        return None
    return float(m.group(1).replace(".", "").replace(",", "."))


def parse_search_results(html: str) -> list[dict]:
    # kleinanzeigen.de ist auf ein neues (Astro/Tailwind-basiertes) Frontend
    # umgestiegen - die alten "aditem"-Klassen gibt es nicht mehr. Die neuen
    # Utility-Klassen sind autogeneriert und instabil, darum wird hier so weit
    # wie moeglich ueber stabilere Signale gegriffen: data-Attribute,
    # Textmuster (PLZ/€/m²) und Alt-Texte statt Klassennamen.
    soup = BeautifulSoup(html, "lxml")
    results = []
    for article in soup.select("article[data-adid]"):
        adid = article.get("data-adid")
        href = article.get("data-href")
        if not adid or not href:
            continue

        # Meist ein <a> im <h3>, manche Karten zeigen den Titel aber ueber ein
        # anklickbares <span> ohne <a> - dann auf den ganzen <h3>-Text ausweichen.
        title_el = article.select_one("h3 a") or article.select_one("h3")
        title = title_el.get_text(strip=True) if title_el else None

        plz, ort = None, None
        for span in article.find_all("span"):
            m = _PLZ_ORT_RE.match(span.get_text(strip=True))
            if m:
                plz, ort = m.group(1), m.group(2)
                break

        # Nur kurze, "strukturiert wirkende" Absaetze beruecksichtigen (z.B.
        # "550 m² · 16 Zi." oder "2.300.000 €") - der lange Beschreibungs-
        # Teaser-Absatz kann inzidentell eine Flaechen-/Preisangabe im
        # Fliesstext enthalten und soll hier nicht faelschlich gewinnen.
        wohnflaeche = None
        preis = None
        for p in article.find_all("p"):
            text = p.get_text(" ", strip=True)
            if len(text) > 60:
                continue
            if wohnflaeche is None:
                wohnflaeche = _parse_m2(text)
            if preis is None:
                preis = _parse_price(text)

        # Gewerbliche Anbieter zeigen eine Firmenzeile (Logo und/oder Name) unter
        # dem Preis, private Inserate haben diesen Block gar nicht. Manche
        # gewerblichen Anbieter zeigen nur den Namen ohne Logo - daher beide
        # Signale pruefen statt nur auf das Logo zu verlassen.
        hat_firmenzeile = article.select_one('img[alt*="Logo des Unternehmens"]') or article.select_one("div.mt-xsmall")
        anbieter_typ = "gewerblich" if hat_firmenzeile else "privat"

        is_top = article.find(lambda tag: tag.name in ("div", "span") and tag.get_text(strip=True) == "TOP") is not None

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
        value_m2 = _parse_m2(value + " m²") if "m²" not in value else _parse_m2(value)
        if "wohnfläche" in key:
            detail["wohnflaeche_m2"] = value_m2
        elif "grundstücksfläche" in key:
            detail["grundstuecksflaeche_m2"] = value_m2
        elif "fläche" in key:
            # generische Fläche (Gewerbeimmobilien: "Fläche", ohne "Wohn-"/"Grundstücks-"-Präfix)
            detail["flaeche_m2_sonstige"] = value_m2
        elif "baujahr" in key:
            m = _YEAR_RE.search(value)
            detail["baujahr"] = int(m.group(1)) if m else None
        elif "etagen" in key:
            detail["etagen"] = value
        elif "zimmer" in key:
            detail["zimmer"] = value
        elif key == "objektart":
            detail["objektart_detail"] = value

    locality_el = soup.select_one("#viewad-locality")
    if locality_el:
        text = locality_el.get_text(strip=True)
        m = re.match(r"(\d{5})\s+(.+)", text)
        if m:
            detail["plz"] = m.group(1)
            rest = m.group(2)
            # Bundesland per Whitelist statt Positions-Raten: kleinanzeigen zeigt hier
            # je nach Objekt/Region mal Bundesland, mal Kreis an ("25335 Kreis Pinneberg -
            # Elmshorn") - und ein naives Split am ersten "-" schneidet Namen mit
            # eigenem Bindestrich (Baden-Württemberg, Nordrhein-Westfalen, ...) falsch ab.
            bundesland = next((b for b in _BUNDESLAENDER if b in rest), None)
            detail["bundesland"] = bundesland
            ort = rest.replace(bundesland, "", 1) if bundesland else rest
            detail["ort"] = ort.strip(" -") or None

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
    # Ein einzelner HTTP-Fehler (429/5xx/Timeout) soll ebenfalls einen erneuten
    # Versuch bekommen statt die ganze Kategorie sofort aufzugeben - genau das
    # hat schon einmal eine komplette Kategorie faelschlich auf "0 Treffer"
    # gesetzt und darüber Inserate als "nicht mehr gelistet" markiert.
    for attempt in range(retries + 1):
        html = get(url)
        results = parse_search_results(html) if html is not None else []
        if results:
            return results
        if attempt < retries:
            grund = "kein HTTP-Erfolg" if html is None else "0 Treffer"
            print(f"  {grund} bei {url} (Versuch {attempt + 1}/{retries + 1}), erneuter Versuch...")
    return []


def fetch_search_results(path: str) -> list[dict]:
    all_results = []
    page_size = None  # aus Seite 1 ableiten statt fest zu verdrahten (war 25,
    # das neue Frontend liefert 27/Seite - eine harte Zahl faellt sonst bei
    # der naechsten Layout-Aenderung wieder aus dem Ruder)
    for page in range(1, config.MAX_PAGES_PER_SEARCH + 1):
        page_results = _fetch_page_with_retry(_page_url(path, page))
        if not page_results:
            break
        all_results.extend(page_results)
        if page_size is None:
            page_size = len(page_results)
        elif len(page_results) < page_size:
            break  # kuerzer als vorherige Seiten -> letzte Seite erreicht
    return all_results


def fetch_detail(url: str) -> dict:
    html = get(url)
    if html is None:
        return {}
    detail = parse_detail(html)
    # Ein abgelaufenes Inserat leitet auf eine Kategorie-Seite um; requests
    # folgt dem Redirect automatisch und parse_detail() findet dort keine
    # Detail-Elemente - kommt also leer zurueck, ohne dass "get" das als
    # Fehler erkennen wuerde (Statuscode ist 200, nur die falsche Seite).
    if not detail:
        print(f"  [leere Detailseite, evtl. abgelaufen/umgeleitet] {url}")
    return detail
