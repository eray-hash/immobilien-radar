import json
import os
from datetime import datetime, timezone

from . import ai_assessment, config, scoring
from .kleinanzeigen import fetch_detail, fetch_search_results


RETRYABLE_KI_STATUS = {"kein_api_key", "fehler"}


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

    for search in config.SEARCHES:
        print(f"Suche: {search['label']} ({search['path']})")
        cards = fetch_search_results(search["path"])
        print(f"  {len(cards)} Treffer (alle Anbieter)")

        for card in cards:
            adid = card["id"]
            seen_ids.add(adid)

            if adid in existing:
                existing[adid]["zuletzt_gesehen"] = now
                existing[adid]["preis_eur"] = card["preis_eur"] or existing[adid].get("preis_eur")
                # kein_api_key/fehler sind keine endgültigen Zustände (im Gegensatz zu
                # "ok" und "zu_wenig_text") - erneut versuchen, z.B. wenn der Key
                # zwischenzeitlich hinterlegt wurde oder ein API-Fehler transient war.
                ki_status = existing[adid].get("ki_einschaetzung", {}).get("status")
                if ki_status in RETRYABLE_KI_STATUS:
                    print(f"  KI-Retry: {existing[adid]['title']}")
                    existing[adid]["ki_einschaetzung"] = ai_assessment.assess_listing(existing[adid])
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

    for adid, listing in existing.items():
        if adid not in seen_ids:
            listing["status"] = "nicht_mehr_in_trefferliste"
        else:
            listing.pop("status", None)

    _save(existing, now)
    print(f"Fertig: {len(existing)} Inserate in {config.OUTPUT_FILE}")


if __name__ == "__main__":
    main()
