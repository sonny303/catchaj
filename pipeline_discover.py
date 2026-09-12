"""Agent-Discovery: Market Scanner for Senior Healthcare Product Management roles.

Uses JobSpy and targeted queries to discover relevant positions across ATS platforms.
Enforces composite SHA-256 deduplication: hash(company + title + location).
"""

import hashlib
import json
import re
import urllib.parse
from datetime import datetime, timezone, timedelta
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
        import sys
        sys.modules["config"] = _mod
        _spec.loader.exec_module(_mod)
        settings = _mod.settings
    else:
        raise

from jobspy import scrape_jobs
from sheets_client import is_posted_within_24h

DISCOVERED_CACHE_PATH = settings.truth_doc_path.parent / "discovered_jobs_cache.json"

def compute_job_hash(company: str, title: str, location: str) -> str:
    """Compute composite SHA-256 hash for deduplication."""
    raw = f"{company.strip().lower()}|{title.strip().lower()}|{location.strip().lower()}"
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()

def detect_ats_platform(url: str) -> str:
    """Classify the ATS platform based on the posting URL."""
    url_lower = url.lower()
    if "greenhouse.io" in url_lower:
        return "Greenhouse"
    elif "lever.co" in url_lower:
        return "Lever"
    elif "ashbyhq.com" in url_lower:
        return "Ashby"
    elif "smartrecruiters.com" in url_lower:
        return "SmartRecruiters"
    elif "myworkdayjobs.com" in url_lower or "workday" in url_lower:
        return "Workday"
    elif "taleo.net" in url_lower:
        return "Taleo"
    elif "icims.com" in url_lower:
        return "iCIMS"
    elif "successfactors" in url_lower:
        return "SuccessFactors"
    return "Other"

def load_cached_hashes() -> set[str]:
    """Load previously seen job hashes from local cache."""
    if DISCOVERED_CACHE_PATH.exists():
        try:
            data = json.loads(DISCOVERED_CACHE_PATH.read_text(encoding="utf-8"))
            return set(data.keys())
        except Exception:
            return set()
    return set()

def save_to_cache(new_jobs: list[dict]):
    """Save discovered jobs to local cache indexed by hash."""
    cache = {}
    if DISCOVERED_CACHE_PATH.exists():
        try:
            cache = json.loads(DISCOVERED_CACHE_PATH.read_text(encoding="utf-8"))
        except Exception:
            cache = {}

    for j in new_jobs:
        cache[j["job_hash"]] = j

    DISCOVERED_CACHE_PATH.write_text(json.dumps(cache, indent=2), encoding="utf-8")

def parse_relative_date(date_str: str) -> tuple[str, bool]:
    """Parse relative time strings like '1h', '6h', '1d', '2d', '2mo' into ISO date and 24h flag."""
    now = datetime.now(timezone.utc)
    m = re.match(r"^(\d+)\s*(mo|w|d|h|m|y)", date_str.strip().lower())
    if not m:
        return now.strftime("%Y-%m-%d"), True
    val, unit = int(m.group(1)), m.group(2)
    if unit in ("h", "m"):
        return now.strftime("%Y-%m-%d"), True
    elif unit == "d":
        dt = now - timedelta(days=val)
        return dt.strftime("%Y-%m-%d"), (val <= 1)
    elif unit == "w":
        dt = now - timedelta(weeks=val)
        return dt.strftime("%Y-%m-%d"), False
    elif unit == "mo":
        dt = now - timedelta(days=val * 30)
        return dt.strftime("%Y-%m-%d"), False
    return now.strftime("%Y-%m-%d"), False

def scrape_hiring_cafe(
    search_term: str = "Healthcare Product Manager",
    location: str = "USA",
    hours_old: int = 24,
    max_results: int = 15,
) -> list[dict]:
    """Scrape recent openings from HiringCafe (hiringcafe.com)."""
    print(f"[*] [HiringCafe] Scraping for '{search_term}' (hours_old={hours_old})...")
    jobs = []
    try:
        from playwright.sync_api import sync_playwright

        days_buffer = 2 if hours_old <= 24 else max(2, hours_old // 24)
        search_state = {
            "searchQuery": search_term,
            "dateFetchedPastNDays": days_buffer,
            "sortBy": "date",
        }
        encoded = urllib.parse.quote(json.dumps(search_state))
        url = f"https://hiringcafe.com/?searchState={encoded}"

        with sync_playwright() as p:
            browser = p.chromium.launch(
                headless=True,
                args=["--disable-blink-features=AutomationControlled", "--no-sandbox"],
            )
            context = browser.new_context(
                user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36"
            )
            page = context.new_page()
            page.goto(url, wait_until="domcontentloaded", timeout=15000)
            page.wait_for_timeout(4000)

            cards_data = page.evaluate(
                """() => {
                const allA = Array.from(document.querySelectorAll('a'));
                const jobLinks = allA.filter(a => a.href && a.href.includes('/job/'));
                const out = [];
                for (const a of jobLinks) {
                    let parent = a;
                    for (let i = 0; i < 5; i++) {
                        if (parent && parent.parentElement) parent = parent.parentElement;
                    }
                    out.push({
                        url: a.href,
                        text: parent ? parent.innerText : ''
                    });
                }
                return out;
            }"""
            )
            browser.close()

            seen_urls = set()
            for c in cards_data:
                raw_url = c.get("url", "").strip()
                if not raw_url or raw_url in seen_urls:
                    continue
                seen_urls.add(raw_url)

                lines = [l.strip() for l in c.get("text", "").split("\n") if l.strip()]
                if len(lines) < 3:
                    continue

                date_raw = lines[0]
                date_posted_str, is_within_24h = parse_relative_date(date_raw)
                if hours_old <= 24 and not is_within_24h:
                    continue

                title = lines[1]
                loc = lines[2]
                company = "Unknown"
                desc = ""
                is_remote_val = False

                for line in lines[3:]:
                    if "remote" in line.lower():
                        is_remote_val = True
                    if ":" in line and company == "Unknown":
                        company = line.split(":")[0].strip()
                        if "nasdaq" in company.lower() or "nyse" in company.lower():
                            company = company.split("NASDAQ")[0].split("NYSE")[0].strip()
                    elif "yoe" in line.lower() or len(line) > 50:
                        desc += " " + line

                if company == "Unknown" and len(lines) > 4:
                    company = lines[4]

                if not title or not company:
                    continue

                if is_remote_val or "remote" in title.lower() or "remote" in loc.lower():
                    if "canada" in loc.lower():
                        loc = "Canada-Remote"
                    else:
                        loc = (
                            f"US-Remote ({loc})"
                            if loc and "remote" not in loc.lower()
                            else "US-Remote"
                        )

                ats = detect_ats_platform(raw_url)
                job_hash = compute_job_hash(company, title, loc)

                jobs.append(
                    {
                        "job_hash": job_hash,
                        "title": title,
                        "company": company,
                        "location": loc,
                        "url": raw_url,
                        "ats_platform": ats,
                        "description": desc.strip(),
                        "date_posted": date_posted_str,
                        "is_remote": is_remote_val or ("remote" in title.lower()),
                        "source": "HiringCafe",
                    }
                )

                if len(jobs) >= max_results:
                    break

        print(
            f"[✓] [HiringCafe] Discovered {len(jobs)} postings within {hours_old}h window."
        )
    except Exception as e:
        print(f"[!] [HiringCafe] Scraper exception encountered: {e}")
    return jobs

def scan_jobs(
    search_term: str = "Healthcare Product Manager",
    location: str = "USA",
    results_wanted: int = 15,
    hours_old: int = 24,
) -> list[dict]:
    """Run market scan across JobSpy (LinkedIn, Indeed, Glassdoor, ZipRecruiter) and HiringCafe."""
    print(
        f"[*] Scanning market for term: '{search_term}' | Location: {location} | Hours: {hours_old} | Target: {results_wanted}"
    )
    seen_hashes = load_cached_hashes()
    discovered = []

    # 1. Scrape HiringCafe
    hiring_cafe_jobs = scrape_hiring_cafe(
        search_term=search_term,
        location=location,
        hours_old=hours_old,
        max_results=results_wanted,
    )
    for j in hiring_cafe_jobs:
        if j["job_hash"] not in seen_hashes:
            discovered.append(j)
            seen_hashes.add(j["job_hash"])

    # 2. Scrape JobSpy
    try:
        jobs_df = scrape_jobs(
            site_name=["indeed", "linkedin", "zip_recruiter", "glassdoor"],
            search_term=search_term,
            location=location,
            results_wanted=results_wanted,
            hours_old=hours_old,
            country_indeed="USA",
            is_remote=True,
        )
    except Exception as e:
        print(f"[!] JobSpy scraper exception encountered: {e}")
        jobs_df = None

    if jobs_df is not None and not jobs_df.empty:
        for _, row in jobs_df.iterrows():
            title = str(row.get("title", "")).strip()
            company = str(row.get("company", "")).strip()
            loc = str(row.get("location", "Remote")).strip()
            job_url = str(row.get("job_url", "")).strip()
            desc = str(row.get("description", "")).strip()
            is_remote_val = bool(row.get("is_remote", False))
            if is_remote_val or "remote" in title.lower() or "remote" in loc.lower():
                if "canada" in loc.lower():
                    loc = "Canada-Remote"
                else:
                    loc = (
                        f"US-Remote ({loc})"
                        if loc and "remote" not in loc.lower()
                        else "US-Remote"
                    )

            if not title or not company:
                continue

            job_hash = compute_job_hash(company, title, loc)
            if job_hash in seen_hashes:
                continue

            date_posted_val = str(row.get("date_posted", "") or "").strip()
            if date_posted_val and date_posted_val.lower() not in [
                "none",
                "nan",
                "nat",
            ]:
                date_posted_val = date_posted_val[:10]
                if hours_old <= 24 and not is_posted_within_24h(date_posted_val, max_hours=hours_old):
                    continue
            else:
                date_posted_val = datetime.now(timezone.utc).strftime("%Y-%m-%d") if hours_old <= 24 else ""

            ats = detect_ats_platform(job_url)
            job_data = {
                "job_hash": job_hash,
                "title": title,
                "company": company,
                "location": loc,
                "url": job_url,
                "ats_platform": ats,
                "description": desc,
                "date_posted": date_posted_val,
                "is_remote": is_remote_val or ("remote" in title.lower()),
                "source": "JobSpy",
            }
            discovered.append(job_data)
            seen_hashes.add(job_hash)

    print(f"[✓] Total discovered {len(discovered)} new unique postings.")
    save_to_cache(discovered)
    return discovered

if __name__ == "__main__":
    scan_jobs(results_wanted=5, hours_old=24)
