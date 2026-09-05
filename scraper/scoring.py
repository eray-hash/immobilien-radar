from __future__ import annotations

import re
import statistics

from . import config


def classify_renovation(title: str, beschreibung: str) -> str:
    text = f"{title or ''} {beschreibung or ''}".lower()
    # Reihenfolge wichtig: spezifischere/negativere Treffer zuerst prüfen,
    # damit "modernisierungsbedürftig" nicht als "modernisiert" erkannt wird.
    # Substring-Vergleich mit einer gezielten Ausnahme: "saniert" soll nicht
    # mitten in "unsaniert" treffen, ABER sehr wohl in "vollsaniert",
    # "teilsaniert", "grundsaniert", "durchsaniert" etc. - eine allgemeine
    # fuehrende Wortgrenze (\b) hatte genau diese haeufigen zusammengesetzten
    # Formulierungen faelschlich mitblockiert. Negatives Lookbehind gezielt
    # nur fuer das Praefix "un" statt einer generellen Wortgrenze.
    # Negierte Formulierungen wie "nicht renoviert" tauchen als eigene Phrasen
    # in RENOVATION_KEYWORDS["sanierungsbeduerftig"] auf (s. config.py).
    for label in ["sanierungsbeduerftig", "neubau", "frisch_saniert", "saniert_modernisiert"]:
        for kw in config.RENOVATION_KEYWORDS[label]:
            if re.search(r"(?<!un)" + re.escape(kw), text):
                return label
    return "unbekannt"


def _region_key(listing: dict) -> str | None:
    plz = listing.get("plz")
    if plz and len(plz) >= 2:
        return plz[:2]
    return None


def _best_flaeche(listing: dict) -> float | None:
    # Wohnfläche ist die aussagekräftigste Bezugsgröße für Häuser/Wohnungen;
    # bei Gewerbe/Grundstücken/Garagen gibt es keine Wohnfläche, dort auf die
    # generische bzw. Grundstücksfläche ausweichen.
    for key in ("wohnflaeche_m2", "flaeche_m2_sonstige", "grundstuecksflaeche_m2"):
        value = listing.get(key)
        if value:
            return value
    return None


def attach_price_assessments(listings: list[dict]) -> None:
    priced = []
    for l in listings:
        flaeche = _best_flaeche(l)
        if l.get("preis_eur") and flaeche and flaeche > 0:
            l["preis_pro_m2"] = round(l["preis_eur"] / flaeche, 2)
            priced.append(l)

    # Preis/m² nur innerhalb desselben Objekttyps vergleichen - ein Mehrfamilienhaus
    # und ein Garagen-Stellplatz haben völlig unterschiedliche m²-Preisniveaus.
    by_region: dict[tuple[str, str], list[float]] = {}
    by_bundesland: dict[tuple[str, str], list[float]] = {}
    for l in priced:
        objekt_typ = l.get("objekt_typ", "unbekannt")
        region = _region_key(l)
        if region:
            by_region.setdefault((objekt_typ, region), []).append(l["preis_pro_m2"])
        bl = l.get("bundesland")
        if bl:
            by_bundesland.setdefault((objekt_typ, bl), []).append(l["preis_pro_m2"])

    MIN_SAMPLE = 3

    for l in listings:
        if l.get("preis_pro_m2") is None:
            l["preis_einschaetzung"] = {
                "label": "keine_daten",
                "hinweis": "Preis oder Fläche fehlt im Inserat",
            }
            continue

        objekt_typ = l.get("objekt_typ", "unbekannt")
        region = _region_key(l)
        region_values = by_region.get((objekt_typ, region), []) if region else []
        bl = l.get("bundesland")
        bl_values = by_bundesland.get((objekt_typ, bl), []) if bl else []

        if len(region_values) >= MIN_SAMPLE:
            basis = f"PLZ-Region {region}, gleicher Objekttyp (n={len(region_values)})"
            median = statistics.median(region_values)
        elif len(bl_values) >= MIN_SAMPLE:
            basis = f"{bl}, gleicher Objekttyp (n={len(bl_values)})"
            median = statistics.median(bl_values)
        else:
            l["preis_einschaetzung"] = {
                "label": "zu_wenig_vergleichsdaten",
                "hinweis": "Noch zu wenig gescrapte Vergleichsobjekte desselben Typs in der Region",
            }
            continue

        abweichung_pct = round((l["preis_pro_m2"] - median) / median * 100, 1)
        if abweichung_pct <= -15:
            label = "guenstig"
        elif abweichung_pct >= 15:
            label = "teuer"
        else:
            label = "im_rahmen"

        l["preis_einschaetzung"] = {
            "label": label,
            "vergleichsbasis": basis,
            "median_preis_pro_m2": round(median, 2),
            "abweichung_pct": abweichung_pct,
        }
