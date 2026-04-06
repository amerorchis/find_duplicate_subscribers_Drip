# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Finds duplicate email subscribers in a Drip email marketing account. Emails that differ only by dots or `+` aliases (e.g. Gmail ignores dots) are flagged as duplicates. Results are saved to an Excel spreadsheet and emailed to recipients. Designed to run as a cron job via `drip_dupes.sh`.

## Running

```bash
# Full pipeline: fetch subscribers, find dupes, save spreadsheet, email report
python main.py
```

## Required Environment Variables

- `DRIP_TOKEN` — Drip API bearer token
- `DRIP_ACCOUNT` — Drip account ID
- `FROM_ALERT_EMAIL` — Gmail address used to send reports
- `FROM_ALERT_PWD` — Gmail app password for SMTP
- `RECIPS` — Comma-separated recipient emails (e.g. `'alice@example.com, bob@example.com'`)

## Architecture

Pipeline flow (`main.py`):
1. **drip.py** — `DripEmailUtil` fetches all subscriber emails from the Drip API using threaded pagination
2. **separate_by_letter.py** — Groups emails by first character (bucketing for parallel comparison)
3. **multiprocess.py** — Runs duplicate checks across letter buckets using `multiprocessing.Pool`
4. **find_dupes.py** — `are_emails_equivalent()` normalizes emails (strips dots for non-Outlook/Hotmail/Yahoo, strips `+` aliases) and compares; `check_equivalence()` does O(n²) pairwise comparison within a bucket
5. **save_excel.py** — Writes duplicate pairs to an Excel file via pandas
6. **send_email.py** — Emails the spreadsheet as an attachment via Gmail SMTP

Output spreadsheets are saved to `files/` with date-stamped names.

## Dependencies

Key packages: `requests`, `pandas`, `openpyxl`
