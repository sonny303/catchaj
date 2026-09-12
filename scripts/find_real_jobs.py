import urllib.request
import json

gh_boards = [
    "oscar", "springhealth", "carbonhealth", "particlehealth", "ribbonhealth",
    "redox", "healthie", "truveta", "innovaccer", "commure", "propellerhealth",
    "clarifyhealth", "tempus", "benchling", "caredx", "aetion",
    "komodohealth", "hingehealth", "ro", "noom", "capsule", "modernhealth",
    "suki", "regard", "elationhealth", "akido", "kyruus", "cedar", "omadahealth",
    "flatiron", "doximity", "cityblockhealth", "headway", "mavenclinic"
]

results = []

for b in gh_boards:
    try:
        url = f"https://boards-api.greenhouse.io/v1/boards/{b}/jobs"
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=4) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            for j in data.get("jobs", []):
                t = j.get("title", "")
                if "product" in t.lower() and ("manager" in t.lower() or "lead" in t.lower() or "director" in t.lower()):
                    loc = j.get("location", {}).get("name", "Remote")
                    results.append({
                        "ats": "Greenhouse",
                        "company": b.title(),
                        "title": t,
                        "location": loc,
                        "url": j.get("absolute_url")
                    })
    except Exception:
        pass

ashby_boards = [
    "canvas-medical", "healthie", "sonar", "metriport", "zushealth",
    "vital", "athelas", "curai", "ophelia", "carebridge", "coda", "plaid",
    "forward", "maven", "nava", "pearlhealth", "picnichealth", "plenful",
    "mainstreethealth", "vanta", "ansarada", "retool"
]

for b in ashby_boards:
    try:
        url = f"https://api.ashbyhq.com/posting-api/job-board/{b}"
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=4) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            for j in data.get("jobs", []):
                t = j.get("title", "")
                if "product" in t.lower() and ("manager" in t.lower() or "lead" in t.lower() or "director" in t.lower()):
                    loc = j.get("location", "Remote")
                    results.append({
                        "ats": "Ashby",
                        "company": b.title(),
                        "title": t,
                        "location": loc,
                        "url": j.get("jobUrl")
                    })
    except Exception:
        pass

print(f"Total live matching PM roles found: {len(results)}")
for r in results:
    print(f"[{r['ats']}] {r['company']} | {r['title']} | {r['location']}")
    print(f"  URL: {r['url']}")
