from __future__ import annotations

import os

import anthropic

MIN_TEXT_LENGTH = 40
MODEL = "claude-haiku-4-5"

SYSTEM_PROMPT = """Du bist ein erfahrener Immobilieninvestor, der Kaufobjekte fuer eine \
Kapitalanlage (Kauf, ggf. Sanierung, anschliessender Verkauf oder Vermietung) einschaetzt.

Du bekommst strukturierte Eckdaten sowie den Inseratstext einer Immobilienanzeige. \
Gib eine knappe Einschaetzung in 2-4 Saetzen auf Deutsch:
- Wirkt der Preis im Verhaeltnis zu den genannten Eckdaten plausibel, eher guenstig \
oder eher teuer?
- Was faellt bei Zustand, Vermietungssituation oder Entwicklungspotenzial auf?
- Worauf sollte man bei einer Besichtigung besonders achten?

Bleib nuechtern und faktenbasiert. Keine Kaufempfehlung, keine Uebertreibungen. \
Bewerte NICHT die Wohnlage/Gegend (dazu liegen dir keine verlaesslichen Daten vor). \
Antworte ausschliesslich mit dem Fliesstext der Einschaetzung, ohne Einleitung, \
Ueberschrift oder Aufzaehlungszeichen."""


def _client() -> anthropic.Anthropic | None:
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        return None
    return anthropic.Anthropic(api_key=api_key)


def assess_listing(listing: dict) -> dict:
    beschreibung = (listing.get("beschreibung") or "").strip()
    if len(beschreibung) < MIN_TEXT_LENGTH:
        return {"status": "zu_wenig_text"}

    client = _client()
    if client is None:
        return {"status": "kein_api_key"}

    facts = "\n".join(
        [
            f"Titel: {listing.get('title')}",
            f"Ort: {listing.get('plz')} {listing.get('ort')}",
            f"Preis: {listing.get('preis_eur')} EUR",
            f"Wohnflaeche: {listing.get('wohnflaeche_m2')} m2",
            f"Preis pro m2: {listing.get('preis_pro_m2')} EUR",
            f"Baujahr: {listing.get('baujahr')}",
            f"Anbietertyp: {listing.get('anbieter_typ')}",
        ]
    )
    user_content = f"{facts}\n\nInseratstext:\n{beschreibung}"

    try:
        response = client.messages.create(
            model=MODEL,
            max_tokens=400,
            system=SYSTEM_PROMPT,
            messages=[{"role": "user", "content": user_content}],
        )
    except anthropic.APIError as e:
        print(f"  [KI-Einschaetzung fehlgeschlagen: {e}]")
        return {"status": "fehler"}

    text = "".join(block.text for block in response.content if block.type == "text").strip()
    if not text:
        return {"status": "fehler"}
    return {"status": "ok", "text": text}
