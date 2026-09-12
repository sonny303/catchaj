"""Google Sheets Pipeline Client (Applications_Pipeline).

Handles Google Sheet read/write operations via gspread, with graceful fallback
to local CSV storage if service account credentials are not yet configured.
"""

import os
import csv
import json
import importlib.util
from pathlib import Path
from datetime import datetime, timezone, timedelta
import re
import gspread
from google.oauth2.service_account import Credentials

# Load settings from config.py if present, or fall back to config.example.py in template mode
try:
    from config import settings
except ImportError:
    _example_cfg = Path(__file__).resolve().parent / "config.example.py"
    if _example_cfg.exists():
        _spec = importlib.util.spec_from_file_location("config", _example_cfg)
        _mod = importlib.util.module_from_spec(_spec)
        import sys
        sys.modules["config"] = _mod
        _spec.loader.exec_module(_mod)
        settings = _mod.settings
    else:
        raise

LOCAL_CACHE_PATH = settings.truth_doc_path.parent / "applications_pipeline_local.csv"

COLUMNS = [
    "Job Title",                  # A
    "Company",                    # B
    "Location / Type",            # C
    "Match Score",                # D
    "Match Rationale & Gaps",     # E
    "Posting URL",                # F
    "ATS Platform",               # G
    "Status",                     # H
    "Drafted Application Q&A",    # I
    "Targeted Bullets",           # J
    "Date Posted",                # K
    "Source",                     # L
    "Audit Log / Timestamp"       # M
]

def is_posted_within_24h(date_str: str, audit_str: str = "", max_hours: int = 24) -> bool:
    """Check whether a posting was posted within the last max_hours (default: 24h)."""
    if not date_str and not audit_str:
        return False
    now_utc = datetime.now(timezone.utc)

    # 1. Evaluate explicit Date Posted
    if date_str and str(date_str).strip().lower() not in ("none", "nan", "nat", ""):
        s = str(date_str).strip()
        # Relative strings like '1h', '6h', '1d', '2d', '2mo'
        rel_match = re.match(r"^(\d+)\s*(mo|month|months|w|week|weeks|d|day|days|h|hr|hour|hours|m|min|minute|minutes)", s.lower())
        if rel_match:
            val, unit = int(rel_match.group(1)), rel_match.group(2)
            if unit in ("h", "hr", "hour", "hours", "m", "min", "minute", "minutes"):
                return True
            if unit in ("d", "day", "days"):
                return val <= (1 if max_hours <= 24 else max_hours // 24)
            return False
        if "today" in s.lower() or "recent" in s.lower() or "just now" in s.lower():
            return True
        if "yesterday" in s.lower():
            return True

        # Parse ISO date YYYY-MM-DD
        iso_match = re.search(r"(\d{4})-(\d{2})-(\d{2})", s)
        if iso_match:
            try:
                y, m, d = int(iso_match.group(1)), int(iso_match.group(2)), int(iso_match.group(3))
                time_match = re.search(r"(\d{2}):(\d{2}):(\d{2})", s)
                if time_match:
                    hh, mm, ss = int(time_match.group(1)), int(time_match.group(2)), int(time_match.group(3))
                    dt = datetime(y, m, d, hh, mm, ss, tzinfo=timezone.utc)
                    diff = (now_utc - dt).total_seconds() / 3600.0
                    return -2.0 <= diff <= float(max_hours)
                else:
                    posted_date = datetime(y, m, d, tzinfo=timezone.utc).date()
                    now_date = now_utc.date()
                    days_diff = (now_date - posted_date).days
                    return 0 <= days_diff <= 1
            except Exception:
                pass
        return False

    # 2. Fallback to audit timestamp if Date Posted was blank
    if audit_str:
        iso_match = re.search(r"(\d{4})-(\d{2})-(\d{2})", str(audit_str))
        time_match = re.search(r"(\d{2}):(\d{2}):(\d{2})", str(audit_str))
        if iso_match and time_match:
            try:
                y, m, d = int(iso_match.group(1)), int(iso_match.group(2)), int(iso_match.group(3))
                hh, mm, ss = int(time_match.group(1)), int(time_match.group(2)), int(time_match.group(3))
                dt = datetime(y, m, d, hh, mm, ss, tzinfo=timezone.utc)
                diff = (now_utc - dt).total_seconds() / 3600.0
                return -2.0 <= diff <= float(max_hours)
            except Exception:
                pass

    return False

class SheetsClient:
    def __init__(self):
        self.sheet_id = settings.google_sheet_id
        self.sa_path = settings.google_service_account_path
        self.tab_name = settings.sheet_tab_name
        self.client = None
        self.worksheet = None
        self.is_connected = False
        self._init_connection()

    def _init_connection(self):
        """Try connecting to Google Sheets API, otherwise fallback to local CSV."""
        if not self.sa_path.exists():
            print(f"[!] Google service account JSON not found at {self.sa_path}. Operating in local CSV fallback mode.")
            self._ensure_local_csv()
            return

        try:
            scopes = [
                "https://www.googleapis.com/auth/spreadsheets",
                "https://www.googleapis.com/auth/drive",
            ]
            creds = Credentials.from_service_account_file(str(self.sa_path), scopes=scopes)
            self.client = gspread.authorize(creds)
            spreadsheet = self.client.open_by_key(self.sheet_id)
            
            try:
                self.worksheet = spreadsheet.worksheet(self.tab_name)
            except gspread.WorksheetNotFound:
                # Create worksheet if missing
                self.worksheet = spreadsheet.add_worksheet(title=self.tab_name, rows=500, cols=len(COLUMNS))
                self.worksheet.append_row(COLUMNS)
                print(f"[+] Created worksheet tab '{self.tab_name}' with schema headers.")

            self.is_connected = True
            print(f"[✓] Connected to Google Sheet: {spreadsheet.title} (Tab: {self.tab_name})")
        except Exception as e:
            print(f"[!] Could not connect to Google Sheets ({e}). Falling back to local storage: {LOCAL_CACHE_PATH}")
            self.is_connected = False
            self._ensure_local_csv()

    def _ensure_local_csv(self):
        """Ensure local CSV cache exists with standard headers."""
        if not LOCAL_CACHE_PATH.exists():
            with open(LOCAL_CACHE_PATH, "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow(COLUMNS)
            print(f"[+] Initialized local pipeline cache at {LOCAL_CACHE_PATH}")

    def get_all_rows(self, only_last_24h: bool = True) -> list[dict]:
        """Fetch all rows from Google Sheets or local CSV.
        If only_last_24h is True, filters to only return jobs posted within the last 24h.
        """
        if self.is_connected and self.worksheet:
            records = self.worksheet.get_all_records()
            if only_last_24h:
                return [r for r in records if is_posted_within_24h(r.get("Date Posted", ""), r.get("Audit Log / Timestamp", ""))]
            return records

        self._ensure_local_csv()
        rows = []
        with open(LOCAL_CACHE_PATH, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for r in reader:
                if only_last_24h:
                    if is_posted_within_24h(r.get("Date Posted", ""), r.get("Audit Log / Timestamp", "")):
                        rows.append(r)
                else:
                    rows.append(r)
        return rows

    def purge_jobs_older_than(self, max_hours: int = 24) -> int:
        """Purge and remove any jobs prior that have not been posted within the last max_hours.
        Returns the count of purged jobs.
        """
        all_rows = self.get_all_rows(only_last_24h=False)
        fresh_rows = []
        purged_count = 0

        for r in all_rows:
            date_posted = r.get("Date Posted", "")
            audit_ts = r.get("Audit Log / Timestamp", "")
            if is_posted_within_24h(date_posted, audit_ts, max_hours=max_hours):
                fresh_rows.append(r)
            else:
                purged_count += 1
                print(f"[x] Purging older job: {r.get('Company')} - {r.get('Job Title')} (Posted: {date_posted or 'Unknown'})")

        if self.is_connected and self.worksheet:
            try:
                self.worksheet.clear()
                rows_to_insert = [COLUMNS]
                for r in fresh_rows:
                    rows_to_insert.append([r.get(c, "") for c in COLUMNS])
                self.worksheet.append_rows(rows_to_insert)
                print(f"[✓] Google Sheet synced: removed {purged_count} jobs older than {max_hours}h. Kept {len(fresh_rows)}.")
            except Exception as e:
                print(f"[!] Error updating Google Sheet during purge: {e}")

        # Always update local CSV cache
        self._ensure_local_csv()
        with open(LOCAL_CACHE_PATH, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=COLUMNS, extrasaction="ignore")
            writer.writeheader()
            for r in fresh_rows:
                r.setdefault("Source", "")
                writer.writerow(r)

        print(f"[✓] Pipeline purged: removed {purged_count} jobs older than {max_hours}h. Remaining in pipeline: {len(fresh_rows)}.")
        return purged_count

    def get_existing_hashes_or_urls(self) -> set[str]:
        """Get set of existing posting URLs for deduplication."""
        rows = self.get_all_rows(only_last_24h=False)
        urls = set()
        for r in rows:
            url = r.get("Posting URL", "").strip()
            if url:
                urls.add(url)
        return urls

    def append_application(self, row_data: dict) -> bool:
        """Append a newly qualified application row."""
        timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")
        ordered_values = [
            row_data.get("Job Title", ""),
            row_data.get("Company", ""),
            row_data.get("Location / Type", ""),
            row_data.get("Match Score", 0),
            row_data.get("Match Rationale & Gaps", ""),
            row_data.get("Posting URL", ""),
            row_data.get("ATS Platform", "Other"),
            row_data.get("Status", "New"),
            row_data.get("Drafted Application Q&A", ""),
            row_data.get("Targeted Bullets", ""),
            row_data.get("Date Posted", ""),
            row_data.get("Source", "JobSpy"),
            f"Added at {timestamp}",
        ]

        if self.is_connected and self.worksheet:
            try:
                self.worksheet.append_row(ordered_values)
                print(f"[✓] Appended to Google Sheet: {row_data.get('Company')} - {row_data.get('Job Title')}")
                return True
            except Exception as e:
                print(f"[!] Error writing to Google Sheet: {e}")

        # Local CSV write
        self._ensure_local_csv()
        with open(LOCAL_CACHE_PATH, "a", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(ordered_values)
        print(f"[✓] Saved locally to CSV: {row_data.get('Company')} - {row_data.get('Job Title')}")
        return True

    def update_row_status(self, row_index: int, status: str, qa_content: str = None, bullets: str = None, date_posted: str = None) -> bool:
        """Update status and drafted content for a given row index (1-indexed)."""
        timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")
        if self.is_connected and self.worksheet:
            try:
                # Column H is Status (col 8)
                self.worksheet.update_cell(row_index, 8, status)
                if qa_content is not None:
                    # Column I is Drafted Q&A (col 9)
                    self.worksheet.update_cell(row_index, 9, qa_content)
                if bullets is not None:
                    # Column J is Bullets (col 10)
                    self.worksheet.update_cell(row_index, 10, bullets)
                if date_posted is not None:
                    # Column K is Date Posted (col 11)
                    self.worksheet.update_cell(row_index, 11, date_posted)
                # Column M is Audit Log (col 13)
                self.worksheet.update_cell(row_index, 13, f"Updated to {status} at {timestamp}")
                return True
            except Exception as e:
                print(f"[!] Error updating row in Google Sheet: {e}")

        # Local update
        rows = self.get_all_rows(only_last_24h=False)
        # Adjusted for 0-indexed data list (row 1 was header)
        idx = row_index - 2
        if 0 <= idx < len(rows):
            rows[idx]["Status"] = status
            if qa_content is not None:
                rows[idx]["Drafted Application Q&A"] = qa_content
            if bullets is not None:
                rows[idx]["Targeted Bullets"] = bullets
            if date_posted is not None:
                rows[idx]["Date Posted"] = date_posted
            rows[idx]["Audit Log / Timestamp"] = f"Updated to {status} at {timestamp}"

            with open(LOCAL_CACHE_PATH, "w", newline="", encoding="utf-8") as f:
                writer = csv.DictWriter(f, fieldnames=COLUMNS, extrasaction="ignore")
                writer.writeheader()
                for r in rows:
                    r.setdefault("Source", "")
                    writer.writerow(r)
            return True
        return False
