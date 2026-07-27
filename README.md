# Automation Toolkit

A few example automations from my freelance work. I'm a certified automation engineer (IHK) and electrical engineering student. My day job used to be automating production lines, these days I also build custom scrapers, data pipelines and workflow automations for small businesses.

**Hire me for:** Python scripts, web scraping, Excel/report automation, AI chatbots, n8n/Make workflows. English & Deutsch.

## What's here

| Tool | Purpose |
|---|---|
| [`scraper_template.py`](scraper_template.py) | Web scraper that plays by the rules: checks robots.txt, rate limits itself, retries on errors. Writes clean CSV. |
| [`excel_report.py`](excel_report.py) | Takes a messy spreadsheet export and turns it into a clean report with totals and group stats. Built for the "3 hours of Excel every Monday" problem. |
| [`deal_scanner.py`](deal_scanner.py) | The real one: a config-driven marketplace monitor I actually run every day for my own refurbishing side business. Watches classified-ad searches, filters by price caps, removes duplicate reposts, reads the full descriptions and grades every listing GOOD/check/AVOID based on keyword rules (for example "already repaired" is a red flag, "battery worn out" means an easy fix). Spits out a ranked Markdown report. |

## How I work

- Polite scraping only. robots.txt, rate limits and site terms are respected. If a site says no, the answer is no.
- Every project ships with a README, a config file and a support window. No handover, no invoice.
- Boring reliability over clever one-liners. Explicit error handling, logging, code you can read in a year.

## Quick start

```bash
pip install requests beautifulsoup4 lxml pandas openpyxl
python scraper_template.py --help
python excel_report.py --help
python deal_scanner.py --config deal_scanner.config.json
```
