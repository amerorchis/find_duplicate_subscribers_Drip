# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Finds duplicate email subscribers in a Drip email marketing account. Emails that differ only by dots or `+` aliases (e.g. Gmail ignores dots) are flagged as duplicates. Results are saved to an Excel spreadsheet and emailed to recipients. Designed to run as a cron job via `drip_dupes.sh`.

## Running

```bash
# Full pipeline: fetch subscribers, find dupes, save spreadsheet, email report
uv run main.py
```

## Required Environment Variables

- `DRIP_TOKEN` — Drip API bearer token
- `DRIP_ACCOUNT` — Drip account ID
- `FROM_ALERT_EMAIL` — Gmail address used to send reports
- `FROM_ALERT_PWD` — Gmail app password for SMTP
- `RECIPS` — Comma-separated recipient emails (e.g. `'alice@example.com, bob@example.com'`)

Optional: set `DRY_RUN=1` to run the full pipeline (fetch + spreadsheet) but skip the email send. Always use this when testing — a normal run emails real recipients.

## Architecture

Pipeline flow (`main.py`):
1. **drip.py** — `DripEmailUtil` fetches all subscriber emails from the Drip API using a bounded thread pool (`ThreadPoolExecutor`) over paginated requests
2. **find_dupes.py** — `normalize_email()` lowercases, strips `+` aliases, and strips dots for Gmail domains only (where dots are insignificant); `find_duplicates()` groups emails by normalized form in O(n) and returns `(normalized, [variants])` groups, skipping unparseable addresses
3. **save_excel.py** — Writes one row per duplicate group to an Excel file via openpyxl
4. **send_email.py** — Emails the spreadsheet to each recipient over a single Gmail SMTP session

`main.py` validates all required environment variables up front and creates `files/` if missing. Output spreadsheets are saved to `files/` with date-stamped names.

## Testing

```bash
uv run pytest
```

## Dependencies

Key packages: `requests`, `openpyxl` (all pure Python — no compiled dependencies, so installs work on 32-bit ARM)
