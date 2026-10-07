#!/usr/bin/env python3
"""
Diagnostic script #2 - inspect the actual structure of individual listing
cards (title/price/area per apartment or house) on mogi.vn's listing pages,
before writing a real parser against them.

Usage:
    pip install requests beautifulsoup4 certifi
    python debug_listings.py

Paste the full printed output back.
"""
import re

import certifi
import requests
from bs4 import BeautifulSoup

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml",
}

# Listing links end in "-idNNNNNNN" - use that to find each listing anchor.
LISTING_HREF_RE = re.compile(r"-id\d+/?$")


def fetch(url):
    resp = requests.get(url, headers=HEADERS, timeout=15, verify=certifi.where())
    return resp.status_code, resp.text


def inspect(name, url):
    print(f"\n{'=' * 60}\n{name} ({url})\n{'=' * 60}")
    status, html = fetch(url)
    print(f"HTTP status: {status}, response length: {len(html)} chars")

    soup = BeautifulSoup(html, "html.parser")
    anchors = [a for a in soup.find_all("a", href=True) if LISTING_HREF_RE.search(a["href"])]
    print(f"Found {len(anchors)} listing-like <a> tags (href ending in -idNNNN)")

    for a in anchors[:3]:
        print(f"\n--- listing anchor: href={a['href']}")
        print(f"    anchor tag name: <{a.name}>, class={a.get('class')}")
        print(f"    anchor text: {a.get_text(' ', strip=True)[:100]!r}")

        # walk up a few ancestor levels and show each one's tag/class/text,
        # so we can see exactly where price/area/rooms live in the DOM
        node = a
        for level in range(1, 5):
            node = node.parent
            if node is None:
                break
            text = node.get_text(" ", strip=True)
            print(f"    ancestor level {level}: <{node.name} class={node.get('class')}> "
                  f"text[:200]={text[:200]!r}")


if __name__ == "__main__":
    inspect("Apartments (Hanoi)", "https://mogi.vn/ha-noi/mua-can-ho-chung-cu")
    inspect("Houses (Hanoi)", "https://mogi.vn/ha-noi/mua-nha")
