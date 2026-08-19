from __future__ import annotations

import statistics

from . import config


def classify_renovation(title: str, beschreibung: str) -> str:
    text = f"{title or ''} {beschreibung or ''}".lower()
    # Reihenfolge wichtig: spezifischere/negativere Treffer zuerst prüfen,
    # damit "modernisierungsbedürftig" nicht als "modernisiert" erkannt wird.
    for label in ["sanierungsbeduerftig", "neubau", "frisch_saniert", "saniert_modernisiert"]:
        for kw in config.RENOVATION_KEYWORDS[label]:
            if kw in text:
                return label
    return "unbekannt"


def _region_key(listing: dict) -> str | None:
    plz = listing.get("plz")
    if plz and len(plz) >= 2:
        return plz[:2]
    return None


def attach_price_assessments(listings: list[dict]) -> None:
    priced = [
        l
        for l in listings
        if l.get("preis_eur") and l.get("wohnflaeche_m2") and l["wohnflaeche_m2"] > 0
    ]
    for l in priced:
        l["preis_pro_m2"] = round(l["preis_eur"] / l["wohnflaeche_m2"], 2)

    by_region: dict[str, list[float]] = {}
    by_bundesland: dict[str, list[float]] = {}
    for l in priced:
        region = _region_key(l)
        if region:
            by_region.setdefault(region, []).append(l["preis_pro_m2"])
        bl = l.get("bundesland")
        if bl:
            by_bundesland.setdefault(bl, []).append(l["preis_pro_m2"])

    MIN_SAMPLE = 3

    for l in listings:
        if l.get("preis_pro_m2") is None:
            l["preis_einschaetzung"] = {
                "label": "keine_daten",
                "hinweis": "Preis oder Wohnfläche fehlt im Inserat",
            }
            continue

        region = _region_key(l)
        region_values = by_region.get(region, []) if region else []
        bl = l.get("bundesland")
        bl_values = by_bundesland.get(bl, []) if bl else []

        if len(region_values) >= MIN_SAMPLE:
            basis = f"PLZ-Region {region} (n={len(region_values)})"
            median = statistics.median(region_values)
        elif len(bl_values) >= MIN_SAMPLE:
            basis = f"{bl} (n={len(bl_values)})"
            median = statistics.median(bl_values)
        else:
            l["preis_einschaetzung"] = {
                "label": "zu_wenig_vergleichsdaten",
                "hinweis": "Noch zu wenig gescrapte Vergleichsobjekte in der Region",
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
