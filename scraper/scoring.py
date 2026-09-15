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


# --- Kostenlose, regelbasierte Investment-Einschätzung ("Lukrativität") ---
# Ersetzt keine echte Bewertung nach dem Master-Prompt "Professionelle
# Immobilienbewertung" (der echte Unterlagen wie Grundbuch/Mietverträge
# braucht), sondern überträgt dessen Grundprinzip - Chancen und Risiken
# transparent und nachvollziehbar statt pauschal zu benennen - auf das, was
# aus dem frei zugänglichen Inseratstext ohne KI-Aufruf ableitbar ist.

# Jahresnettokaltmiete direkt genannt, z.B. "Jahresnettokaltmiete von 45.600€"
# oder "...von ca. € 32.700,00" - das €-Zeichen steht je nach Formulierung vor
# oder nach dem Betrag, daher hier bewusst nicht als Teil des Musters verankert.
_JAHRESMIETE_RE = re.compile(r"jahres(?:netto)?kaltmiete[^\d]{0,20}([\d.]+(?:,\d+)?)", re.IGNORECASE)
# Monatsmiete explizit als "monatliche (Netto-)Kaltmiete" benannt.
_MONATSMIETE_RE = re.compile(
    r"monatlich[e]?\s+(?:netto)?kaltmiete[^\d]{0,20}([\d.]+(?:,\d+)?)", re.IGNORECASE
)
# Generischer Betrag direkt vor "Kaltmiete", z.B. "590,00 € Kaltmiete" - kann
# bei mehreren Einheiten im selben Text mehrfach vorkommen (dann summiert).
_MIETE_BETRAG_RE = re.compile(
    r"([\d.]+(?:,\d+)?)\s*(?:€|euro)\s*(?:netto)?kaltmiete", re.IGNORECASE
)

RISK_LABELS = {
    "erbbaurecht": "Erbbaurecht/Erbpacht erwähnt – kein Grundstückseigentum, laufende Erbpachtzahlungen prüfen",
    "zwangsversteigerung": "Zwangs-/Teilungsversteigerung erwähnt – besondere rechtliche Rahmenbedingungen prüfen",
    "denkmalschutz": "Denkmalschutz erwähnt – Nutzungs-/Sanierungsauflagen möglich",
    "altlasten": "Altlasten/Kontamination erwähnt – Bodengutachten anfordern",
    "leerstand": "Leerstand erwähnt – Mietausfallrisiko",
    "mietrueckstand": "Mietrückstände erwähnt",
    "bauschaden": "Bauschäden/Feuchtigkeit/Schimmel erwähnt – technische Prüfung empfohlen",
    "belegungsbindung": "Belegungs-/Mietpreisbindung erwähnt – eingeschränkte Vermarktbarkeit",
    "eigentuemerstruktur": "Erbengemeinschaft/mehrere Eigentümer erwähnt – Vertretungsvollmachten klären",
}

POTENTIAL_LABELS = {
    "baurecht_gesichert": "Baugenehmigung laut Inserat bereits vorhanden",
    "ausbaureserve": "Ausbaureserve (z. B. Dachgeschoss) laut Inserat vorhanden",
    "teilbar": "Teilung/WEG-Teilung laut Inserat möglich",
    "erweiterung": "Erweiterung (Anbau/Aufstockung) laut Inserat möglich",
    "nachverdichtung": "Nachverdichtungs-/Neubaugebietslage laut Inserat",
    "stabil_vermietet": "Langjährig/stabil vermietet laut Inserat",
}

# Master-Prompt-Abschnitt 23 ("Fehlende Unterlagen"), reduziert auf die immer
# gültigen Basics plus objekttypspezifische Ergänzung - eine vollständige
# Auflistung braucht echte Unterlagen zur Prüfung, hier geht es nur um den
# Hinweis, was vor einem Ankauf zusätzlich angefordert werden sollte.
_BASE_FEHLENDE_UNTERLAGEN = [
    "Aktueller Grundbuchauszug",
    "Nachweis Wohn-/Nutzflächenberechnung",
    "Energieausweis",
]
_TYP_FEHLENDE_UNTERLAGEN = {
    "wohnung": [
        "Teilungserklärung inkl. Nachträge",
        "Protokolle der letzten Eigentümerversammlungen",
        "Wirtschaftsplan/Jahresabrechnung",
    ],
    "mehrfamilienhaus": [
        "Rent Roll / vollständige Mieterliste",
        "Aktuelle Mietverträge",
        "Nebenkostenabrechnung",
    ],
    "gewerbe_buero": ["Mietverträge inkl. Nachträge", "Nachweis genehmigte Nutzung"],
    "gewerbe_weitere": ["Mietverträge inkl. Nachträge", "Nachweis genehmigte Nutzung"],
    "gewerbe_lager": ["Mietverträge inkl. Nachträge", "Nachweis genehmigte Nutzung"],
    "gewerbe_gastro": ["Mietverträge inkl. Nachträge", "Betriebserlaubnis/Konzession"],
    "gewerbe_einzelhandel": ["Mietverträge inkl. Nachträge", "Nachweis genehmigte Nutzung"],
    "grundstueck": [
        "Bebauungsplan / Auskunft Bauamt",
        "Auszug Baulastenverzeichnis",
        "Erschließungsnachweis",
    ],
}


def _parse_de_zahl(raw: str) -> float:
    value = raw.replace(".", "").replace(",", ".")
    return float(value) if value else 0.0


def extract_jahresmiete(beschreibung: str | None) -> float | None:
    if not beschreibung:
        return None
    m = _JAHRESMIETE_RE.search(beschreibung)
    if m:
        jahresmiete = _parse_de_zahl(m.group(1))
        # Ohne direkten Waehrungsanker (siehe Regex-Kommentar) kann hier auch
        # eine themafremde Zahl in Reichweite von "Kaltmiete" gematcht werden
        # (z.B. ein Datum/Verweis) - unplausible Werte lieber verwerfen statt
        # eine falsche Rendite auszuweisen.
        return jahresmiete if 500 <= jahresmiete <= 2_000_000 else None
    m = _MONATSMIETE_RE.search(beschreibung)
    if m:
        monatsmiete = _parse_de_zahl(m.group(1))
        return round(monatsmiete * 12, 2) if 50 <= monatsmiete <= 50_000 else None
    # Nur Beträge unterhalb einer plausiblen Monatsmieten-Obergrenze summieren -
    # groessere, bereits als Jahresbetrag gemeinte Zahlen vor "Kaltmiete" wuerden
    # durch die Hochrechnung *12 sonst grotesk verfaelscht.
    monatsbetraege = [_parse_de_zahl(x) for x in _MIETE_BETRAG_RE.findall(beschreibung)]
    monatsbetraege = [b for b in monatsbetraege if 0 < b < 6000]
    if monatsbetraege:
        return round(sum(monatsbetraege) * 12, 2)
    return None


def _keyword_treffer(text: str, keyword_dict: dict[str, list[str]]) -> list[str]:
    return [kategorie for kategorie, keywords in keyword_dict.items() if any(kw in text for kw in keywords)]


def attach_investment_score(listings: list[dict]) -> None:
    for l in listings:
        text = f"{l.get('title') or ''} {l.get('beschreibung') or ''}".lower()
        score = 0
        chancen: list[str] = []
        risiken: list[str] = []

        einschaetzung = l.get("preis_einschaetzung") or {}
        price_label = einschaetzung.get("label")
        abw = einschaetzung.get("abweichung_pct")
        if price_label == "guenstig":
            score += 2
            basis = einschaetzung.get("vergleichsbasis", "")
            chancen.append(
                f"Kaufpreis {abs(abw):.0f}% unter Vergleichsniveau ({basis})" if abw is not None else "Kaufpreis unter Vergleichsniveau"
            )
        elif price_label == "teuer":
            score -= 2
            basis = einschaetzung.get("vergleichsbasis", "")
            risiken.append(
                f"Kaufpreis {abw:.0f}% über Vergleichsniveau ({basis})" if abw is not None else "Kaufpreis über Vergleichsniveau"
            )

        sanierungsstand = l.get("sanierungsstand")
        if sanierungsstand in ("neubau", "frisch_saniert"):
            score += 1
            chancen.append("Neuwertiger bzw. frisch sanierter Zustand laut Inserat")
        elif sanierungsstand == "sanierungsbeduerftig":
            score -= 1
            risiken.append("Sanierungsbedarf laut Inserat – CAPEX vor Ankauf kalkulieren")

        risk_hits = _keyword_treffer(text, config.RISK_KEYWORDS)
        for kategorie in risk_hits[:4]:
            score -= 1
            risiken.append(RISK_LABELS[kategorie])

        potential_hits = _keyword_treffer(text, config.POTENTIAL_KEYWORDS)
        for kategorie in potential_hits[:4]:
            score += 1
            chancen.append(POTENTIAL_LABELS[kategorie])

        jahresmiete = extract_jahresmiete(l.get("beschreibung"))
        rendite = None
        if l.get("preis_eur") and jahresmiete and l["preis_eur"] > 0:
            rendite = round(jahresmiete / l["preis_eur"] * 100, 2)
            # Renditen ueber 20% sind auf dem deutschen Markt praktisch nie
            # real und fast immer ein Parsing-Artefakt (z.B. ein themafremder
            # Betrag im Fliesstext, der zufaellig in Reichweite von
            # "Kaltmiete" lag) - dann lieber "keine Angabe" als eine falsche
            # Zahl als vermeintliche Chance ausweisen.
            if rendite > 20:
                rendite = None
        if rendite is not None:
            hinweis = f"Bruttoanfangsrendite ca. {rendite}% laut Mietangabe im Inserat (IST, ungeprüft)"
            if rendite >= 6:
                score += 2
                chancen.append(hinweis)
            elif rendite < 3:
                score -= 1
                risiken.append(f"Niedrige {hinweis[0].lower()}{hinweis[1:]}")
            else:
                chancen.append(hinweis)

        hat_genug_daten = price_label not in (None, "keine_daten") or rendite is not None or risk_hits or potential_hits
        if not hat_genug_daten:
            label = "zu_wenig_daten"
        elif score >= 4:
            label = "sehr_interessant"
        elif score >= 2:
            label = "interessant"
        elif score <= -4:
            label = "unattraktiv"
        elif score <= -2:
            label = "eher_unattraktiv"
        else:
            label = "neutral"

        objekt_typ = l.get("objekt_typ", "")
        fehlende_unterlagen = _BASE_FEHLENDE_UNTERLAGEN + _TYP_FEHLENDE_UNTERLAGEN.get(objekt_typ, [])

        l["lukrativitaet"] = {
            "score": score,
            "label": label,
            "chancen": chancen[:6],
            "risiken": risiken[:6],
            "rendite_brutto_pct": rendite,
            "fehlende_unterlagen": fehlende_unterlagen,
        }
