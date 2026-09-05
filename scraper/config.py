BASE_URL = "https://www.kleinanzeigen.de"

# Jede Suche ist ein eigener robots.txt-Bucket mit bis zu 5 erlaubten Seiten
# (siehe MAX_PAGES_PER_SEARCH). "path" ist der Pfad ab der Domain, wie er auch
# beim Klicken durch die Kategorie/Filter auf kleinanzeigen.de entsteht -
# verifiziert per Browser, keine geratenen URLs.
SEARCHES = [
    # Häuser zum Kauf, Fokus Mehrfamilienhaus/Rendite
    {
        "objekt_typ": "mehrfamilienhaus",
        "label": "Mehrfamilienhaus",
        "path": "s-haus-kaufen/mehrfamilienhaus/k0c208",
    },
    {
        "objekt_typ": "mehrfamilienhaus",
        "label": "Mehrfamilienhaus",
        "path": "s-haus-kaufen/zinshaus/k0c208",
    },
    {
        "objekt_typ": "mehrfamilienhaus",
        "label": "Mehrfamilienhaus",
        "path": "s-haus-kaufen/renditeobjekt/k0c208",
    },
    # Eigentumswohnungen (Kategorie ist bereits kaufen-only)
    {
        "objekt_typ": "wohnung",
        "label": "Eigentumswohnung",
        "path": "s-wohnung-kaufen/c196",
    },
    # Gewerbeimmobilien, Art:Kaufen, je Objektart eine eigene Suche
    {
        "objekt_typ": "gewerbe_buero",
        "label": "Büro/Praxis",
        "path": "s-gewerbeimmobilien/kaufen/c277+gewerbeimmobilien.art_s:kaufen"
        "+gewerbeimmobilien.objektart_s:bueros_praxen",
    },
    {
        "objekt_typ": "gewerbe_weitere",
        "label": "Weitere Gewerbeeinheit",
        "path": "s-gewerbeimmobilien/kaufen/c277+gewerbeimmobilien.art_s:kaufen"
        "+gewerbeimmobilien.objektart_s:gewerbeeinheit",
    },
    {
        "objekt_typ": "gewerbe_lager",
        "label": "Lager/Halle/Produktion",
        "path": "s-gewerbeimmobilien/kaufen/c277+gewerbeimmobilien.art_s:kaufen"
        "+gewerbeimmobilien.objektart_s:lager_hallen_produktion",
    },
    {
        "objekt_typ": "gewerbe_gastro",
        "label": "Gastronomie/Hotel",
        "path": "s-gewerbeimmobilien/kaufen/c277+gewerbeimmobilien.art_s:kaufen"
        "+gewerbeimmobilien.objektart_s:gastronomie_hotels",
    },
    {
        "objekt_typ": "gewerbe_einzelhandel",
        "label": "Einzelhandel/Kiosk",
        "path": "s-gewerbeimmobilien/kaufen/c277+gewerbeimmobilien.art_s:kaufen"
        "+gewerbeimmobilien.objektart_s:einzelhandel_kioske",
    },
    # Grundstücke: robots.txt blockiert den Art/Typ-URL-Filter (grundstuecke_garten.art_s
    # und .type_s), daher über Keyword auf Baugrundstück eingegrenzt statt per Filter.
    # Es können vereinzelt Mietangebote mit reinrutschen, das lässt sich nicht ausschließen.
    {
        "objekt_typ": "grundstueck",
        "label": "Baugrundstück",
        "path": "s-grundstuecke-garten/baugrundstueck/k0c207",
    },
    # Garagen & Stellplätze, Art:Kaufen
    {
        "objekt_typ": "garage_stellplatz",
        "label": "Garage/Stellplatz",
        "path": "s-garage-lagerraum/kaufen/c197+garage_lagerraum.art_s:kaufen",
    },
]

# "Neubauprojekte" (c403) bewusst ausgelassen: nutzt ein komplett anderes
# Karten-Layout (Preisspannen über mehrere Einheiten statt article.aditem) und
# würde einen eigenen Parser brauchen - bei nur ~100 Treffern bundesweit aktuell
# nicht im Verhältnis zum Aufwand.

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
        # negierte Formulierungen ("nicht renoviert" etc.) - "saniert"/"renoviert"/
        # "modernisiert" wären sonst als Teilstring-Treffer faelschlich positiv erkannt
        "unsaniert",
        "unrenoviert",
        "nicht saniert",
        "nicht renoviert",
        "nicht modernisiert",
        "nie saniert",
        "nie renoviert",
        "nie modernisiert",
    ],
}
