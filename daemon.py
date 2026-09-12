"""Background Auto-Scraper Daemon.

Runs continuously on a configurable interval (default: every 60 minutes),
scans for target healthcare PM roles, triages matches, appends to the pipeline,
dispatches email alerts, and auto-tailors applications.
"""

import time
import threading
import importlib.util
from datetime import datetime
from pathlib import Path

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

from sheets_client import SheetsClient
from pipeline_discover import scan_jobs
from pipeline_evaluate import process_and_triage_job
from pipeline_tailor import process_tailoring_pipeline

# Construct queries dynamically from search settings or use defaults
_titles = getattr(settings.search, "target_titles", ["Product Manager"])[:3]
_domains = getattr(settings.search, "target_domains", ["Technology"])[:2]
SEARCH_QUERIES = [
    f"{title} {domain} Remote".strip()
    for title in _titles
    for domain in _domains
] if _titles and _domains else [
    "Senior Product Manager Healthcare Remote",
    "Lead Product Manager Healthcare Remote",
    "Staff Product Manager Healthcare",
    "Principal Product Manager Healthcare",
    "Director Product Management Digital Health",
]

class ScraperDaemon:
    def __init__(self, interval_minutes: int = 60):
        self.interval_seconds = interval_minutes * 60
        self.is_running = False
        self.thread = None
        self.last_run_time = None
        self.last_run_status = "Idle"
        self.jobs_discovered_count = 0
        self.jobs_qualified_count = 0

    def run_single_cycle(self):
        """Execute one complete discovery, evaluation, and tailoring pass."""
        self.last_run_status = "Scanning"
        self.last_run_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"\n[DAEMON] Starting automated market scan cycle at {self.last_run_time}...")
        
        client = SheetsClient()
        new_qualified = 0
        total_discovered = 0

        for query in SEARCH_QUERIES:
            try:
                print(f"[DAEMON] Querying (past 24h): '{query}'...")
                discovered = scan_jobs(search_term=query, location="USA", results_wanted=6, hours_old=24)
                total_discovered += len(discovered)
                for j in discovered:
                    if process_and_triage_job(j, client):
                        new_qualified += 1
            except Exception as e:
                print(f"[DAEMON] Error during query '{query}': {e}")
            time.sleep(1)

        self.jobs_discovered_count += total_discovered
        self.jobs_qualified_count += new_qualified

        if new_qualified > 0:
            print(f"[DAEMON] Running auto-tailoring for {new_qualified} new qualified roles...")
            try:
                process_tailoring_pipeline(client)
            except Exception as e:
                print(f"[DAEMON] Tailoring error: {e}")

        self.last_run_status = f"Completed ({new_qualified} new matches)"
        print(f"[DAEMON] Cycle finished. Discovered: {total_discovered} | Qualified: {new_qualified}")

    def _loop(self):
        while self.is_running:
            self.run_single_cycle()
            # Sleep in 5-second increments to respond quickly to stop signal
            for _ in range(self.interval_seconds // 5):
                if not self.is_running:
                    break
                time.sleep(5)

    def start(self):
        if not self.is_running:
            self.is_running = True
            self.thread = threading.Thread(target=self._loop, daemon=True)
            self.thread.start()
            print("[DAEMON] Auto-scraper daemon started.")

    def stop(self):
        self.is_running = False
        self.last_run_status = "Stopped"
        print("[DAEMON] Auto-scraper daemon stopped.")

daemon_instance = ScraperDaemon(interval_minutes=60)

if __name__ == "__main__":
    print("[*] Starting standalone scraper daemon (Ctrl+C to exit)...")
    d = ScraperDaemon(interval_minutes=60)
    d.is_running = True
    d._loop()
