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
_session.headers.update({"User-Agent": config.USER_AGENT, "Accept-Language": "de-DE,de;q=0.9"})


def allowed(url: str) -> bool:
    return _robots.can_fetch(config.USER_AGENT, url)


def get(url: str) -> str | None:
    if not allowed(url):
        print(f"[robots.txt] blockiert, überspringe: {url}")
        return None
    time.sleep(random.uniform(*config.REQUEST_DELAY_SECONDS))
    resp = _session.get(url, timeout=20)
    if resp.status_code != 200:
        print(f"[http {resp.status_code}] {url}")
        return None
    return resp.text
