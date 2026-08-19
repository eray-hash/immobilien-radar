# Immobilien-Radar

Durchsucht [kleinanzeigen.de](https://www.kleinanzeigen.de) automatisiert nach privat angebotenen
Mehrfamilienhaus-/Zinshaus-Objekten und stellt die Treffer als Übersicht bereit.

## Wie es funktioniert

- `scraper/` — Python-Scraper, robots.txt-konform (nur erlaubte URLs/Seiten, keine
  `anbieter:`- oder `sortierung:`-Parameter, da von kleinanzeigen.de per robots.txt gesperrt).
  Anbieter-Typ (privat/gewerblich) wird stattdessen aus dem HTML der Trefferliste gelesen.
- `.github/workflows/scrape.yml` — führt den Scraper 3× täglich per GitHub Actions aus und
  committed die Ergebnisse zurück ins Repo.
- `docs/` — statisches Dashboard (GitHub Pages), liest `docs/data/listings.json` und zeigt
  Titel, Preis, €/m², Baujahr, Sanierungsstand-Einschätzung und eine Preis-Einschätzung im
  Vergleich zu anderen gescrapten Objekten in derselben PLZ-Region/demselben Bundesland.

## Setup

1. Repo auf GitHub anlegen und pushen.
2. In den Repo-Settings unter **Pages** → Source: `Deploy from a branch`, Branch `main`, Ordner `/docs`.
3. Unter **Actions** sicherstellen, dass Workflows aktiviert sind (Actions sind bei neuen Repos
   automatisch aktiv). Der Workflow läuft 3×/Tag automatisch, kann aber auch manuell über
   „Run workflow“ (workflow_dispatch) gestartet werden.
4. Nach dem ersten Lauf ist das Dashboard unter `https://<user>.github.io/<repo>/` erreichbar.

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
