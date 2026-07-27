#!/usr/bin/env python3
"""Marketplace deal scanner — config-driven search monitoring with text analysis.

Monitors classified-ad searches, filters by price caps, deduplicates reposts,
fetches full descriptions, and grades each hit with configurable red/green
keyword patterns (e.g. "already repaired" = red, "battery worn" = green).
Writes a ranked Markdown report.

Built politely: browser-identified UA, configurable delays between requests,
one page per query. Adapt the CSS selectors in `parse_listing` for your target
site; the default config targets a German classifieds site as demo.

Usage:
    python deal_scanner.py --config deal_scanner.config.json --out report.md
"""
from __future__ import annotations

import argparse
import json
import re
import sys
import time
from datetime import datetime
from pathlib import Path

import requests
from bs4 import BeautifulSoup

HEADERS = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:128.0) Gecko/20100101 Firefox/128.0",
    "Accept-Language": "de-DE,de;q=0.9",
}


def parse_price(text: str) -> int | None:
    match = re.search(r"(\d[\d.]*)\s*€", text.replace("\xa0", " "))
    return int(match.group(1).replace(".", "")) if match else None


def parse_listing(ad, base_url: str) -> dict | None:
    link = ad.select_one("a[href^='/s-anzeige/']")
    title_node = ad.select_one("h2") or link
    if not link or not title_node:
        return None
    price_node = ad.select_one("[class*=price]")
    location_node = ad.select_one("[class*=locality]")
    return {
        "title": title_node.get_text(" ", strip=True)[:70],
        "price": parse_price(price_node.get_text(" ", strip=True)) if price_node else None,
        "ort": location_node.get_text(" ", strip=True)[:30] if location_node else "?",
        "url": base_url + link["href"].split("?")[0],
    }


def fetch(url: str, delay: float) -> str:
    time.sleep(delay)
    session = requests.Session()
    session.headers.update(HEADERS)
    response = session.get(url, timeout=30)
    response.raise_for_status()
    return response.text


def grade(description: str, red: re.Pattern, green: re.Pattern) -> str:
    if red.search(description):
        return "AVOID"
    return "GOOD" if green.search(description) else "check"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", required=True)
    parser.add_argument("--out", default="report.md")
    args = parser.parse_args()

    config = json.loads(Path(args.config).read_text(encoding="utf-8"))
    base = config["base_url"]
    delay = config.get("delay_seconds", 6)
    red = re.compile(config["red_flags"], re.IGNORECASE)
    green = re.compile(config["green_flags"], re.IGNORECASE)

    hits, seen = [], set()
    for search in config["searches"]:
        try:
            soup = BeautifulSoup(fetch(base + search["path"], delay), "lxml")
        except requests.RequestException as exc:
            print(f"{search['label']}: FAILED ({exc})", file=sys.stderr)
            continue
        for ad in soup.select("article.aditem"):
            row = parse_listing(ad, base)
            if not row or row["price"] is None or row["price"] > search["max_price"]:
                continue
            key = (row["title"], row["price"], row["ort"])
            if key in seen:
                continue
            seen.add(key)
            row["search"] = search["label"]
            hits.append(row)
        print(f"{search['label']}: {len(hits)} total hits so far", file=sys.stderr)

    for row in hits[: config.get("detail_fetch_cap", 30)]:
        try:
            soup = BeautifulSoup(fetch(row["url"], delay / 2), "lxml")
            node = soup.select_one("#viewad-description-text")
            desc = node.get_text(" ", strip=True) if node else ""
        except requests.RequestException:
            desc = ""
        row["desc"] = desc[:160].replace("|", "/")
        row["verdict"] = grade(desc, red, green)

    order = {"GOOD": 0, "check": 1, "AVOID": 2}
    hits.sort(key=lambda r: (order.get(r.get("verdict", "check"), 1), r["price"]))
    lines = [
        f"# Deal report {datetime.now():%Y-%m-%d %H:%M} — {len(hits)} hits",
        "",
        "| Verdict | Search | Title | Price € | Ort | Description | Link |",
        "|---|---|---|---|---|---|---|",
    ]
    for r in hits:
        lines.append(
            f"| {r.get('verdict', '?')} | {r['search']} | {r['title']} | {r['price']} "
            f"| {r['ort']} | {r.get('desc', '')} | [ad]({r['url']}) |"
        )
    Path(args.out).write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Wrote {len(hits)} hits to {args.out}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
