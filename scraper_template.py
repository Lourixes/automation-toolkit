#!/usr/bin/env python3
"""Polite web scraper template: robots.txt aware, rate-limited, retrying.

Usage:
    python scraper_template.py --url https://example.com/products --selector "h2.title a" --out results.csv
"""
from __future__ import annotations

import argparse
import csv
import logging
import sys
import time
from datetime import datetime, timezone
from urllib import robotparser
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup

USER_AGENT = "PoliteScraper/1.0 (+contact: see repository)"
REQUEST_DELAY_SECONDS = 1.5
MAX_RETRIES = 3
RETRY_BACKOFF_SECONDS = 5

log = logging.getLogger("scraper")


def is_allowed(url: str) -> bool:
    """Check robots.txt before touching a page. If in doubt, stay out."""
    parsed = urlparse(url)
    robots_url = f"{parsed.scheme}://{parsed.netloc}/robots.txt"
    parser = robotparser.RobotFileParser()
    try:
        parser.set_url(robots_url)
        parser.read()
    except OSError:
        log.warning("Could not read %s, treating as disallowed", robots_url)
        return False
    return parser.can_fetch(USER_AGENT, url)


def fetch(session: requests.Session, url: str) -> str | None:
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            response = session.get(url, timeout=20)
            if response.status_code == 429:
                log.warning("Rate limited (429), backing off")
                time.sleep(RETRY_BACKOFF_SECONDS * attempt * 2)
                continue
            response.raise_for_status()
            return response.text
        except requests.RequestException as exc:
            log.warning("Attempt %d/%d failed for %s: %s", attempt, MAX_RETRIES, url, exc)
            time.sleep(RETRY_BACKOFF_SECONDS * attempt)
    log.error("Giving up on %s", url)
    return None


def extract_links(html: str, base_url: str, selector: str) -> list[dict[str, str]]:
    soup = BeautifulSoup(html, "html.parser")
    now = datetime.now(timezone.utc).isoformat()
    rows = []
    for node in soup.select(selector):
        title = node.get_text(strip=True)
        href = node.get("href")
        if not title or not href:
            continue
        rows.append({"title": title, "url": urljoin(base_url, href), "scraped_at": now})
    return rows


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--url", required=True, help="Page to scrape")
    parser.add_argument("--selector", required=True, help="CSS selector for link elements")
    parser.add_argument("--out", default="results.csv", help="Output CSV path")
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")

    if not is_allowed(args.url):
        log.error("robots.txt disallows scraping %s, aborting", args.url)
        return 1

    session = requests.Session()
    session.headers["User-Agent"] = USER_AGENT

    time.sleep(REQUEST_DELAY_SECONDS)
    html = fetch(session, args.url)
    if html is None:
        return 1

    rows = extract_links(html, args.url, args.selector)
    if not rows:
        log.warning("Selector %r matched nothing", args.selector)

    with open(args.out, "w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=["title", "url", "scraped_at"])
        writer.writeheader()
        writer.writerows(rows)

    log.info("Wrote %d rows to %s", len(rows), args.out)
    return 0


if __name__ == "__main__":
    sys.exit(main())
