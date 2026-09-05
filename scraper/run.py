from __future__ import annotations

import json
import os
import re
from datetime import datetime, timezone

from . import ai_assessment, config, scoring
from .kleinanzeigen import fetch_detail, fetch_search_results


RETRYABLE_KI_STATUS = {"kein_api_key", "fehler"}
MAX_KI_RETRIES_PER_RUN = 100

# robots.txt erlaubt pro Kategorie nur 5 Ergebnisseiten (~135 Treffer) - bei
# einem groesseren Archiv (mehrere Tausend Inserate) passt an einem einzelnen
# Tag bei weitem nicht jedes bekannte Inserat in dieses Fenster, auch wenn es
# auf kleinanzeigen.de weiterhin aktiv ist (es rutscht in der Relevanz-/
# Datumssortierung nur unter Seite 5). Ein Inserat erst nach mehreren
# aufeinanderfolgenden Läufen ohne Sichtung als "nicht mehr gelistet" werten,
# statt schon beim ersten Ausbleiben - sonst wandert der Grossteil des
# Archivs binnen weniger Tage faelschlich auf "verschwunden".
MIN_MISSES_BEFORE_DELISTING = 3

# "Gesucht"/Ankauf-Anzeigen sind keine Verkaufsangebote, tauchen aber in
# Kaufen-Kategorien auf (haeufig als Agentur-Massenanzeige, z.B. dieselbe
# "Wir suchen Baugrundstuecke..."-Anzeige dutzendfach) und verzerren sowohl
# das Angebot als auch die Preis-Vergleichsbasis in scoring.py.
_GESUCHT_AD_RE = re.compile(
    r"\b(wir suchen|wir kaufen|ankauf|grundst[üu]cksankauf|immobilienankauf)\b",
    re.IGNORECASE,
)


def _ist_gesucht_anzeige(title: str | None) -> bool:
    return bool(title) and _GESUCHT_AD_RE.search(title) is not None


def _now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def _load_existing() -> dict:
    if not os.path.exists(config.OUTPUT_FILE):
        return {}
    with open(config.OUTPUT_FILE, encoding="utf-8") as f:
        data = json.load(f)
    return {l["id"]: l for l in data.get("listings", [])}


def _save(existing: dict, now: str) -> None:
    # Wird nach jeder Kategorie aufgerufen, nicht erst am Ende - damit ein
    # Abbruch/Timeout mitten im Lauf nicht die bereits abgerufenen (und bei der
    # KI-Einschätzung bereits bezahlten) Inserate verwirft.
    all_listings = list(existing.values())
    scoring.attach_price_assessments(all_listings)

    os.makedirs(os.path.dirname(config.OUTPUT_FILE), exist_ok=True)
    with open(config.OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(
            {"aktualisiert_am": now, "anzahl": len(all_listings), "listings": all_listings},
            f,
            ensure_ascii=False,
            indent=2,
        )


def main() -> None:
    existing = _load_existing()
    seen_ids = set()
    now = _now()
    ki_retries_left = MAX_KI_RETRIES_PER_RUN

    for search in config.SEARCHES:
        print(f"Suche: {search['label']} ({search['path']})")
        cards = fetch_search_results(search["path"])
        print(f"  {len(cards)} Treffer (alle Anbieter)")

        for card in cards:
            if _ist_gesucht_anzeige(card.get("title")):
                continue

            adid = card["id"]
            seen_ids.add(adid)

            if adid in existing:
                existing[adid]["zuletzt_gesehen"] = now
                existing[adid]["preis_eur"] = card["preis_eur"] or existing[adid].get("preis_eur")
                # kein_api_key/fehler sind keine endgültigen Zustände (im Gegensatz zu
                # "ok" und "zu_wenig_text") - erneut versuchen, z.B. wenn der Key
                # zwischenzeitlich hinterlegt wurde oder ein API-Fehler transient war.
                ki_status = existing[adid].get("ki_einschaetzung", {}).get("status")
                if ki_status in RETRYABLE_KI_STATUS and ki_retries_left > 0:
                    print(f"  KI-Retry: {existing[adid]['title']}")
                    existing[adid]["ki_einschaetzung"] = ai_assessment.assess_listing(existing[adid])
                    ki_retries_left -= 1
                continue

            print(f"  neu: {card['title']}")
            detail = fetch_detail(card["url"])

            listing = {**card, **{k: v for k, v in detail.items() if v is not None}}
            listing["objekt_typ"] = search["objekt_typ"]
            listing["objekt_typ_label"] = search["label"]
            listing["sanierungsstand"] = scoring.classify_renovation(
                listing.get("title"), listing.get("beschreibung")
            )
            listing["lage_hinweis"] = "manuell prüfen"
            listing["erstgesehen"] = now
            listing["zuletzt_gesehen"] = now
            listing["ki_einschaetzung"] = ai_assessment.assess_listing(listing)
            existing[adid] = listing

        _save(existing, now)

    # Sicherheitsnetz gegen falsche Massen-Delistings: wenn in diesem Lauf nur
    # ein winziger Bruchteil der bekannten Inserate wiedergefunden wurde,
    # deutet das auf einen Scraping-Fehler hin (IP-Block, kaputter Parser nach
    # einem Website-Relaunch, ...) statt auf einen echten Markteinbruch -
    # genau das ist schon einmal passiert und hat den ganzen Datenbestand
    # faelschlich als "nicht mehr gelistet" markiert. In diesem Fall lieber
    # nichts markieren als falsch alles.
    min_erwartet = max(5, len(existing) * 0.1)
    if existing and len(seen_ids) < min_erwartet:
        print(
            f"WARNUNG: Nur {len(seen_ids)} von {len(existing)} bekannten Inseraten in diesem Lauf "
            f"gesehen (erwartet mind. {min_erwartet:.0f}) - vermutlich ein Scraping-Fehler. "
            "Ueberspringe das Markieren als 'nicht mehr gelistet'."
        )
    else:
        for adid, listing in existing.items():
            if adid in seen_ids:
                listing["nicht_gesehen_seit_laeufen"] = 0
                listing.pop("status", None)
            else:
                misses = listing.get("nicht_gesehen_seit_laeufen", 0) + 1
                listing["nicht_gesehen_seit_laeufen"] = misses
                if misses >= MIN_MISSES_BEFORE_DELISTING:
                    listing["status"] = "nicht_mehr_in_trefferliste"
                else:
                    # noch nicht oft genug in Folge verpasst - als weiter aktiv
                    # werten statt vorschnell auf "verschwunden" zu setzen
                    listing.pop("status", None)

    _save(existing, now)
    print(f"Fertig: {len(existing)} Inserate in {config.OUTPUT_FILE}")


if __name__ == "__main__":
    main()
