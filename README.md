# Immobilien-Radar

Durchsucht [kleinanzeigen.de](https://www.kleinanzeigen.de) automatisiert nach
Mehrfamilienhaus-/Zinshaus-Objekten (privat und gewerblich) und stellt die Treffer als
Übersicht mit Preis-Einschätzung und KI-Textbewertung bereit.

## Wie es funktioniert

- `scraper/` — Python-Scraper, robots.txt-konform (nur erlaubte URLs/Seiten, keine
  `anbieter:`- oder `sortierung:`-Parameter, da von kleinanzeigen.de per robots.txt gesperrt).
  Anbieter-Typ (privat/gewerblich) wird stattdessen aus dem HTML der Trefferliste gelesen und
  im Dashboard als Filter/Badge angezeigt.
- `scraper/ai_assessment.py` — ruft für jedes neu gefundene Inserat (nicht erneut für bereits
  bekannte, aus Kostengründen) die Claude API (Haiku 4.5) auf und lässt eine kurze
  Investoren-Einschätzung aus Eckdaten + Inseratstext erstellen. Bei fehlendem/zu kurzem Text
  (< 40 Zeichen) wird kein Call gemacht, sondern `status: zu_wenig_text` gesetzt. Braucht das
  Repo-Secret `ANTHROPIC_API_KEY` — ohne Secret läuft der Scraper trotzdem (Status
  `kein_api_key`), nur ohne KI-Text.
- `.github/workflows/scrape.yml` — führt den Scraper 3× täglich per GitHub Actions aus und
  committed die Ergebnisse zurück ins Repo. Manueller Start auch über den "↻ Neuen Scan
  starten"-Button im Dashboard (verlinkt auf die GitHub-Actions-Seite) oder direkt in Actions.
- `docs/` — statisches Dashboard (GitHub Pages), liest `docs/data/listings.json` und zeigt
  Titel, Preis, €/m², Baujahr, Sanierungsstand-Einschätzung, Anbietertyp und KI-Einschätzung.
  Preis-Einschätzung vergleicht gegen andere gescrapte Objekte in derselben PLZ-Region/demselben
  Bundesland.

## Setup

1. Repo auf GitHub anlegen und pushen.
2. In den Repo-Settings unter **Pages** → Source: `Deploy from a branch`, Branch `main`, Ordner `/docs`.
3. Unter **Actions** sicherstellen, dass Workflows aktiviert sind (Actions sind bei neuen Repos
   automatisch aktiv). Der Workflow läuft 3×/Tag automatisch, kann aber auch manuell über
   „Run workflow“ (workflow_dispatch) gestartet werden.
4. Unter **Settings → Secrets and variables → Actions → New repository secret** ein Secret
   namens `ANTHROPIC_API_KEY` mit einem gültigen Anthropic-API-Key anlegen, damit die
   KI-Texteinschätzung funktioniert.
5. Nach dem ersten Lauf ist das Dashboard unter `https://<user>.github.io/<repo>/` erreichbar.

## Lokal ausführen

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python3 -m scraper.run
```

Ergebnis landet in `docs/data/listings.json`. Zum lokalen Anschauen des Dashboards:

```bash
cd docs && python3 -m http.server 8420
```

## Bekannte Einschränkungen (Stand MVP)

- Nur **eBay Kleinanzeigen** wird gescraped (ImmoScout24/Immowelt bewusst ausgeklammert,
  siehe Chat-Verlauf zu rechtlichem Risiko/ToS).
- robots.txt erlaubt nur die Seiten 1–5 pro Suche und keine Sortierparameter — die
  Trefferabdeckung wächst dadurch v.a. über die Zeit (3 Läufe/Tag), nicht durch tiefe Paginierung.
- Die "Preis-Einschätzung" vergleicht nur gegen bereits selbst gescrapte Objekte derselben
  PLZ-Region bzw. desselben Bundeslands — bei wenigen Vergleichsobjekten (Anfangsphase) steht
  "Zu wenig Vergleichsdaten".
- Lage-Qualität (Arbeitgeber, Tourismus, Gegend) wird **nicht** automatisch bewertet — dafür im
  Dashboard bewusst der Hinweis "manuell prüfen".
- Kein Preis- oder Einheiten-Filter — es werden alle Mehrfamilienhaus-/Zinshaus-Inserate ohne
  Ober-/Untergrenze aufgenommen.
