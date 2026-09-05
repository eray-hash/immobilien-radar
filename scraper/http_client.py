from __future__ import annotations

import random
import time
import urllib.robotparser

import requests

from . import config

_robots = urllib.robotparser.RobotFileParser()
_robots.set_url(f"{config.BASE_URL}/robots.txt")
_robots.read()

_session = requests.Session()
# Ein vollstaendigerer, chrome-typischer Header-Satz statt nur UA+Accept-Language -
# requests' Minimal-Header (nur UA, Accept: */*, kein sec-ch-ua/sec-fetch-*) sieht
# fuer Bot-Erkennung (Akamai o.ae.) selbst untypisch genug aus, um eher aufzufallen,
# unabhaengig von der anfragenden IP.
_session.headers.update(
    {
        "User-Agent": config.USER_AGENT,
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
        "Accept-Language": "de-DE,de;q=0.9,en-US;q=0.8,en;q=0.7",
        "Sec-Ch-Ua": '"Chromium";v="124", "Google Chrome";v="124", "Not-A.Brand";v="99"',
        "Sec-Ch-Ua-Mobile": "?0",
        "Sec-Ch-Ua-Platform": '"Windows"',
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "none",
        "Sec-Fetch-User": "?1",
        "Upgrade-Insecure-Requests": "1",
    }
)


def allowed(url: str) -> bool:
    return _robots.can_fetch(config.USER_AGENT, url)


def get(url: str) -> str | None:
    if not allowed(url):
        print(f"[robots.txt] blockiert, überspringe: {url}")
        return None
    time.sleep(random.uniform(*config.REQUEST_DELAY_SECONDS))
    # kleinanzeigen.de setzt nach dem ersten Request ein Akamai-Bot-Tracking-Cookie
    # (_abck), das danach leere Trefferlisten liefert (HTTP 200, aber ohne echte
    # Inhalte) - jeder Request startet daher bewusst ohne mitgeschleppte Cookies.
    _session.cookies.clear()
    try:
        resp = _session.get(url, timeout=20)
    except requests.exceptions.RequestException as e:
        # Netzwerkfehler (Timeout, Verbindungsabbruch, ...) sollen den gesamten
        # Lauf nicht abschießen - einzelne Seite überspringen und weitermachen.
        print(f"[netzwerkfehler] {url}: {e}")
        return None
    if resp.status_code != 200:
        print(f"[http {resp.status_code}] {url}")
        return None
    # kleinanzeigen.de schickt keinen charset in Content-Type mehr, requests
    # faellt dann per HTTP-Spec-Default auf ISO-8859-1 zurueck obwohl der Body
    # tatsaechlich UTF-8 ist - das hat bisher jeden Umlaut/€/m² kaputt gemacht
    # und damit z.B. Preis-Regex (sucht literal "€") ins Leere laufen lassen.
    resp.encoding = "utf-8"
    return resp.text
