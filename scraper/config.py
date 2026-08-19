BASE_URL = "https://www.kleinanzeigen.de"
CATEGORY_ID = 208  # Häuser zum Kauf

# Suchbegriffe für Mehrfamilien-/Renditeobjekte. Mehrere Begriffe erweitern die
# Abdeckung, da robots.txt pro Suche nur die Seiten 1-5 erlaubt (~125 Treffer/Begriff).
SEARCH_KEYWORDS = [
    "mehrfamilienhaus",
    "zinshaus",
    "renditeobjekt",
]

MAX_PAGES_PER_SEARCH = 5  # robots.txt: Disallow /*/seite:6* und höher

REQUEST_DELAY_SECONDS = (1.5, 3.0)  # zufällige Pause zwischen Requests (min, max)

USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/124.0 Safari/537.36"
)

OUTPUT_FILE = "docs/data/listings.json"

# Stichwörter zur groben Einordnung des Sanierungsstands aus Titel/Beschreibung.
RENOVATION_KEYWORDS = {
    "neubau": ["neubau", "erstbezug", "kfw"],
    "frisch_saniert": ["kernsaniert", "vollständig saniert", "komplett saniert", "frisch saniert"],
    "saniert_modernisiert": ["saniert", "modernisiert", "renoviert"],
    "sanierungsbeduerftig": [
        "sanierungsbedürftig",
        "renovierungsbedürftig",
        "entkernt",
        "sanierungsobjekt",
        "sanierungsfall",
        "modernisierungsbedürftig",
    ],
}
