# Automation Toolkit

Example automations from my freelance work: clean, documented, production-minded Python.
I'm a certified automation engineer (IHK) and electrical engineering student — I build
custom scrapers, data pipelines, and workflow automations for small businesses.

**Hire me:** Python scripts · web scraping · Excel/report automation · AI chatbots · n8n/Make workflows.
English & Deutsch.

## What's here

| Tool | Purpose |
|---|---|
| [`scraper_template.py`](scraper_template.py) | Polite, robots.txt-respecting web scraper → CSV. Retry logic, rate limiting, clean structure. |
| [`excel_report.py`](excel_report.py) | Turns raw spreadsheet exports into a formatted summary report (totals, group stats) — the classic "3 hours of Excel every Monday" killer. |

## Principles I work by

- **Polite scraping only** — respects `robots.txt`, rate limits, and site terms.
- **Handover included** — every project ships with a README, config file, and support window.
- **Boring reliability** — explicit error handling, logging, no clever one-liners.

## Quick start

```bash
pip install requests beautifulsoup4 pandas openpyxl
python scraper_template.py --help
python excel_report.py --help
```
