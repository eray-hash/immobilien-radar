# Immobilien-Radar

Durchsucht [kleinanzeigen.de](https://www.kleinanzeigen.de) automatisiert nach
Investment-relevanten Immobilien (privat und gewerblich) und stellt die Treffer als
Übersicht mit Preis-Einschätzung und KI-Textbewertung bereit.

## Kategorien

- Häuser zum Kauf (Mehrfamilienhaus, Zinshaus, Renditeobjekt)
- Eigentumswohnungen
- Gewerbeimmobilien, Art "Kaufen": Büro/Praxis, Weitere Gewerbeeinheiten (u.a. Parkhäuser),
  Lager/Halle/Produktion, Gastronomie/Hotels (u.a. Boardinghäuser), Einzelhandel/Kiosk
- Baugrundstücke
- Garagen & Stellplätze, Art "Kaufen"

Bewusst ausgelassen: **Neubauprojekte** — nutzt ein komplettes anderes Karten-Layout
(Preisspannen über mehrere Einheiten statt Standard-Inserat) und bräuchte einen eigenen
Parser; bei nur ~100 Treffern bundesweit nicht im Verhältnis zum Aufwand.

## Wie es funktioniert

- `scraper/config.py` — `SEARCHES`-Liste: jede Suche hat einen `objekt_typ` (fürs Dashboard-
  Filter), ein `label` und einen verifizierten kleinanzeigen-URL-Pfad. Jede Suche ist ein
  eigener robots.txt-Bucket mit bis zu 5 erlaubten Seiten (`MAX_PAGES_PER_SEARCH`).
- `scraper/http_client.py` — kleinanzeigen.de setzt nach dem ersten Request ein
  Akamai-Bot-Tracking-Cookie (`_abck`), das danach leere Trefferlisten liefert (HTTP 200, aber
  ohne echten Inhalt). Jeder Request löscht daher bewusst vorher alle Cookies der Session.
- `scraper/kleinanzeigen.py` — Parser für Trefferlisten- und Detailseiten. Bundesland wird per
  Whitelist der 16 echten Bundesländer aus dem Standort-Text erkannt (nicht per Positions-Split,
  da kleinanzeigen dort teils Kreis- statt Bundeslandnamen zeigt und Bundesländer mit eigenem
  Bindestrich wie "Baden-Württemberg" sonst falsch abgeschnitten werden).
- `scraper/ai_assessment.py` — ruft für jedes neu gefundene Inserat (nicht erneut für bereits
  bekannte, aus Kostengründen) die Claude API (Haiku 4.5) auf und lässt eine kurze
  Investoren-Einschätzung aus Eckdaten + Inseratstext erstellen. Bei fehlendem/zu kurzem Text
  (< 40 Zeichen) wird kein Call gemacht, sondern `status: zu_wenig_text` gesetzt. Braucht das
  Repo-Secret `ANTHROPIC_API_KEY` — ohne Secret läuft der Scraper trotzdem (Status
  `kein_api_key`), nur ohne KI-Text.
- `scraper/scoring.py` — Preis/m² wird nur innerhalb desselben `objekt_typ` und derselben
  Region verglichen (ein Garagenstellplatz und ein Mehrfamilienhaus haben völlig andere
  €/m²-Niveaus). Fläche fällt zurück auf Wohnfläche → generische Fläche → Grundstücksfläche,
  je nachdem was im Inserat vorhanden ist.
- `scraper/run.py` — speichert nach **jeder** Kategorie zwischen (nicht erst am Ende), damit ein
  Abbruch/Timeout mitten im Lauf nicht die bereits abgerufenen (und bei der KI-Einschätzung
  bereits bezahlten) Inserate verwirft. Inserate, die nicht mehr in den Ergebnissen auftauchen,
  werden mit `status: nicht_mehr_in_trefferliste` markiert, aber **nie gelöscht** — bewusst so,
  weil ein rausgenommenes und später günstiger neu inseriertes Objekt sonst seine Preishistorie
  verlieren würde (relevant für Verhandlungen).
- `.github/workflows/scrape.yml` — führt den Scraper 3× täglich per GitHub Actions aus und
  committed die Ergebnisse zurück ins Repo. Manueller Start auch über den "↻ Neuen Scan
  starten"-Button im Dashboard (verlinkt auf die GitHub-Actions-Seite) oder direkt in Actions.
- `docs/` — statisches Dashboard (GitHub Pages), liest `docs/data/listings.json`. Filter für
  Preis, Fläche, Standort, Objekttyp, Bundesland, Anbietertyp (privat/gewerblich) und
  Preis-Einschätzung.

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

**Achtung Erstlauf:** Beim ersten Lauf mit neuen/erweiterten Kategorien werden alle aktuell
aktiven Inserate als "neu" erkannt und einzeln abgerufen (Detailseite + KI-Einschätzung) —
das kann bei tausenden Treffern deutlich länger dauern (z.B. ~1h bei ~1.400 neuen Inseraten,
bei bewusst vorsichtiger 1,5–3s Pause zwischen Requests). Folgeläufe sind schnell, da nur noch
wirklich neue Inserate seit dem letzten Lauf einzeln abgerufen werden.

## Bekannte Einschränkungen (Stand MVP)

- Nur **eBay Kleinanzeigen** wird gescraped (ImmoScout24/Immowelt bewusst ausgeklammert,
  siehe Chat-Verlauf zu rechtlichem Risiko/ToS).
- robots.txt erlaubt nur die Seiten 1–5 pro Suche und keine Sortierparameter — die
  Trefferabdeckung wächst dadurch v.a. über die Zeit (3 Läufe/Tag), nicht durch tiefe Paginierung.
- **Grundstücke**: robots.txt sperrt den URL-Filter für Kaufen/Mieten und Grundstücksart bei
  dieser Kategorie (`grundstuecke_garten.art_s`/`.type_s`) — die Eingrenzung läuft daher über das
  Suchwort "Baugrundstück" statt über einen Filter, vereinzelte Mietangebote können reinrutschen.
- Die "Preis-Einschätzung" vergleicht nur gegen bereits selbst gescrapte Objekte desselben
  Objekttyps in derselben PLZ-Region bzw. demselben Bundesland — bei wenigen Vergleichsobjekten
  (Anfangsphase) steht "Zu wenig Vergleichsdaten".
- Lage-Qualität (Arbeitgeber, Tourismus, Gegend) wird **nicht** automatisch bewertet — dafür im
  Dashboard bewusst der Hinweis "manuell prüfen".
- Kein Preis- oder Flächen-Filter im Scraper selbst — es werden alle Inserate der jeweiligen
  Kategorie ohne Ober-/Untergrenze aufgenommen (Filterung passiert im Dashboard).
- Bei ca. 17% der Inserate zeigt kleinanzeigen einen Kreis- statt Bundeslandnamen im
  Standort-Text (z.B. "Kreis Pinneberg" statt "Schleswig-Holstein") — dort bleibt das
  Bundesland-Feld leer, der Ort-Name selbst ist aber korrekt.
- Alte/nicht mehr gelistete Inserate werden nie automatisch gelöscht (bewusst, siehe oben) —
  die Altbestände/relistete Objekte derselben Immobilie werden aber nicht automatisch verknüpft,
  das müsste man manuell über Titel/Ort in der Dashboard-Suche erkennen.
