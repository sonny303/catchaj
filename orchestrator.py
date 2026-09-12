"""Lead Orchestrator: Automated, Human-in-the-Loop (HITL) Job Application Engine.

Coordinates the 5 specialized sub-agents:
1. Agent-Truth-Sync   (sync_truth.py)
2. Agent-Discovery    (pipeline_discover.py)
3. Agent-Evaluator    (pipeline_evaluate.py)
4. Agent-Tailor       (pipeline_tailor.py)
5. Agent-Browser      (run_staged_application.py)
"""

import argparse
import sys
import importlib.util
from pathlib import Path

# Load settings from config.py if present, or fall back to config.example.py in template mode
try:
    from config import settings
except ImportError:
    _example_cfg = Path(__file__).resolve().parent / "config.example.py"
    if _example_cfg.exists():
        _spec = importlib.util.spec_from_file_location("config", _example_cfg)
        _mod = importlib.util.module_from_spec(_spec)
        sys.modules["config"] = _mod
        _spec.loader.exec_module(_mod)
        settings = _mod.settings
    else:
        raise

from sheets_client import SheetsClient
from sync_truth import main as run_sync
from pipeline_discover import scan_jobs
from pipeline_evaluate import process_and_triage_job
from pipeline_tailor import process_tailoring_pipeline
from run_staged_application import stage_application

def print_banner():
    allowed_locs = ", ".join(settings.search.allowed_locations)
    target_titles = ", ".join(settings.search.target_titles[:2])
    print(f"""
========================================================================
   CATCHAJ — AGENTIC JOB APPLICATION ENGINE (HITL)
========================================================================
Candidate: {settings.candidate.name} ({target_titles})
Location:  {settings.candidate.current_location} | Remote Targets: {allowed_locs}
ATS Mode:  Frictionless Direct (>={settings.search.score_threshold_frictionless}) | Account Gated (>={settings.search.score_threshold_account_gated})
========================================================================
""")

def show_status():
    client = SheetsClient()
    rows = client.get_all_rows()
    print(f"\n[*] Current Applications Pipeline: {len(rows)} entries")
    if not rows:
        print("    (No applications currently in pipeline)")
        return

    print(f"{'Row':<5} | {'Company':<25} | {'Match':<6} | {'Status':<12} | {'Title':<30}")
    print("-" * 85)
    for idx, r in enumerate(rows, start=2):
        co = (r.get("Company") or "")[:24]
        sc = str(r.get("Match Score") or 0)
        st = (r.get("Status") or "New")[:11]
        ti = (r.get("Job Title") or "")[:29]
        print(f"{idx:<5} | {co:<25} | {sc:<6} | {st:<12} | {ti:<30}")

def run_pipeline_cycle(search_term: str = "Healthcare Product Manager", count: int = 10, hours_old: int = 24):
    client = SheetsClient()
    print("\n--- [Stage 1: Truth-Sync] ---")
    run_sync()

    print(f"\n--- [Stage 2: Discovery & Evaluation (Query: '{search_term}', Hours: {hours_old})] ---")
    discovered = scan_jobs(search_term=search_term, location="USA", results_wanted=count, hours_old=hours_old)
    qualified_count = 0
    for j in discovered:
        if process_and_triage_job(j, client):
            qualified_count += 1
    print(f"[✓] Evaluated {len(discovered)} postings; {qualified_count} passed thresholds.")

    print("\n--- [Stage 3: Application Tailoring] ---")
    process_tailoring_pipeline(client)

    print("\n--- Pipeline Cycle Complete ---")
    show_status()

def main():
    parser = argparse.ArgumentParser(description="Healthcare PM HITL Job Application Engine Orchestrator")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    subparsers.add_parser("status", help="Display current pipeline status and rows")
    subparsers.add_parser("sync", help="Run Agent-Truth-Sync to validate truth doc")
    
    scan_parser = subparsers.add_parser("scan", help="Run Agent-Discovery & Agent-Evaluator")
    scan_parser.add_argument("--query", default="Healthcare Product Manager", help="Search query")
    scan_parser.add_argument("--count", type=int, default=10, help="Results count target")
    scan_parser.add_argument("--hours", type=int, default=24, help="Max hours since job was posted (default: 24)")

    subparsers.add_parser("tailor", help="Run Agent-Tailor on rows with status 'New'")

    add_parser = subparsers.add_parser("add", help="Directly intake a specific job posting by URL")
    add_parser.add_argument("--url", required=True, help="Job posting application URL")
    add_parser.add_argument("--company", required=True, help="Company name")
    add_parser.add_argument("--title", required=True, help="Job title")
    add_parser.add_argument("--location", default="US-Remote", help="Location (default: US-Remote)")
    add_parser.add_argument("--desc", default="", help="Job description snippet or requirements")

    stage_parser = subparsers.add_parser("stage", help="Run Agent-Browser to stage application")
    stage_parser.add_argument("--row", type=int, help="Specific row index to stage (1-indexed)")

    cycle_parser = subparsers.add_parser("cycle", help="Run full cycle: sync -> scan -> evaluate -> tailor")
    cycle_parser.add_argument("--query", default="Healthcare Product Manager")
    cycle_parser.add_argument("--count", type=int, default=10)
    cycle_parser.add_argument("--hours", type=int, default=24)

    args = parser.parse_args()
    print_banner()

    if args.command == "status":
        show_status()
    elif args.command == "sync":
        run_sync()
    elif args.command == "scan":
        client = SheetsClient()
        discovered = scan_jobs(search_term=args.query, location="USA", results_wanted=args.count, hours_old=args.hours)
        for j in discovered:
            process_and_triage_job(j, client)
    elif args.command == "tailor":
        client = SheetsClient()
        process_tailoring_pipeline(client)
    elif args.command == "add":
        from pipeline_discover import detect_ats_platform
        client = SheetsClient()
        ats = detect_ats_platform(args.url)
        job_data = {
            "title": args.title,
            "company": args.company,
            "location": args.location,
            "url": args.url,
            "ats_platform": ats,
            "description": args.desc or f"{args.title} at {args.company}",
            "is_remote": "remote" in args.location.lower() or "remote" in args.title.lower(),
        }
        print(f"[+] Intaking job: {args.company} - {args.title} ({ats})")
        passed = process_and_triage_job(job_data, client)
        if passed:
            print("[+] Running immediate tailoring for newly added role...")
            process_tailoring_pipeline(client)
            show_status()
        else:
            print("[-] Role did not qualify under current location/score rules.")
    elif args.command == "stage":
        client = SheetsClient()
        rows = client.get_all_rows()
        if args.row:
            idx = args.row - 2
            if 0 <= idx < len(rows):
                stage_application(rows[idx], args.row, client)
            else:
                print(f"[-] Row {args.row} out of range.")
        else:
            print("[-] Please specify --row <N> to stage.")
    elif args.command == "cycle":
        run_pipeline_cycle(search_term=args.query, count=args.count)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
