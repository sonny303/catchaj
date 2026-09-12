"""Learning Agent & Adaptive Threshold Calibrator.

Continuously learns candidate preferences from jobs applied to vs. jobs skipped/declined.
Dynamically tunes match scores, keyword affinity weights, and filtering thresholds.
"""

import json
import re
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

LEARNING_PROFILE_PATH = settings.truth_doc_path.parent / "learning_profile.json"

KEYWORD_EXTRACT_PATTERNS = [
    "ai", "lims", "interoperability", "fhir", "hl7", "ehr", "epic", "cerner",
    "rpm", "clinical", "prior-auth", "payer", "billing", "telehealth",
    "b2b", "saas", "hardware", "biotech", "genetics", "medical device",
    "platform", "mobile", "analytics", "data", "revenue cycle"
]

class LearningAgent:
    def __init__(self, profile_path: Path = None):
        self.profile_path = profile_path or LEARNING_PROFILE_PATH
        self.profile = self._load_profile()

    def _default_profile(self) -> dict:
        return {
            "version": 1,
            "calibrated_threshold": settings.search.score_threshold_frictionless,  # Default 75
            "applied_count": 0,
            "declined_count": 0,
            "keyword_weights": {
                "ai": 4,
                "interoperability": 4,
                "fhir": 4,
                "ehr": 4,
            },
            "company_affinity": {},
            "blocked_companies": [],
            "reason_counts": {},
            "recent_actions": [],
        }

    def _load_profile(self) -> dict:
        if self.profile_path.exists():
            try:
                data = json.loads(self.profile_path.read_text(encoding="utf-8"))
                # Merge defaults for any missing keys
                defaults = self._default_profile()
                for k, v in defaults.items():
                    data.setdefault(k, v)
                return data
            except Exception as e:
                print(f"[!] Error loading learning profile ({e}). Rebuilding default.")
        return self._default_profile()

    def _save_profile(self):
        try:
            self.profile_path.write_text(json.dumps(self.profile, indent=2), encoding="utf-8")
        except Exception as e:
            print(f"[!] Error saving learning profile: {e}")

    def _extract_job_keywords(self, job_data: dict) -> list[str]:
        text = f"{job_data.get('title', '')} {job_data.get('description', '')}".lower()
        found = []
        for kw in KEYWORD_EXTRACT_PATTERNS:
            if re.search(r"\b" + re.escape(kw) + r"\b", text):
                found.append(kw)
        return found

    def record_applied(self, job_data: dict) -> dict:
        """Record a successful application action (positive reinforcement)."""
        company = str(job_data.get("Company") or job_data.get("company", "")).strip()
        title = str(job_data.get("Job Title") or job_data.get("title", "")).strip()

        self.profile["applied_count"] += 1
        
        # 1. Company affinity boost
        if company:
            current_aff = self.profile["company_affinity"].get(company, 0)
            self.profile["company_affinity"][company] = min(20, current_aff + 5)

        # 2. Keyword affinity boost
        kws = self._extract_job_keywords(job_data)
        for kw in kws:
            current_wt = self.profile["keyword_weights"].get(kw, 0)
            self.profile["keyword_weights"][kw] = min(15, current_wt + 3)

        # 3. Dynamic threshold tuning
        # Healthy application rate keeps threshold accessible (broad)
        total = self.profile["applied_count"] + self.profile["declined_count"]
        if total >= 3:
            ratio = self.profile["applied_count"] / total
            if ratio > 0.4:
                # User finds good matches; keep threshold open
                self.profile["calibrated_threshold"] = max(70, min(80, self.profile["calibrated_threshold"] - 1))

        # 4. Audit history
        self.profile["recent_actions"].insert(0, {
            "timestamp": datetime.now().isoformat(),
            "action": "applied",
            "company": company,
            "title": title,
            "keywords": kws,
        })
        self.profile["recent_actions"] = self.profile["recent_actions"][:25]
        self._save_profile()
        print(f"[LEARNING] Recorded applied role: {company} - {title}. Calibrated threshold: {self.profile['calibrated_threshold']}%.")
        return self.get_summary()

    def record_declined(self, job_data: dict, reasons: list[str], notes: str = "") -> dict:
        """Record a declined/skipped role (negative reinforcement with reason analysis)."""
        company = str(job_data.get("Company") or job_data.get("company", "")).strip()
        title = str(job_data.get("Job Title") or job_data.get("title", "")).strip()

        self.profile["declined_count"] += 1

        # 1. Tally reasons
        for r in reasons:
            self.profile["reason_counts"][r] = self.profile["reason_counts"].get(r, 0) + 1

        # 2. Handle specific reasons
        if "Not interested in company" in reasons and company:
            if company not in self.profile["blocked_companies"]:
                self.profile["blocked_companies"].append(company)
            self.profile["company_affinity"][company] = -100

        kws = self._extract_job_keywords(job_data)
        if "Tech stack mismatch" in reasons:
            for kw in kws:
                current_wt = self.profile["keyword_weights"].get(kw, 0)
                self.profile["keyword_weights"][kw] = max(-15, current_wt - 4)

        if "Not healthcare/clinical enough" in reasons:
            # Penalize any non-clinical terms detected
            for kw in ["hardware", "biotech", "genetics"]:
                if kw in kws:
                    self.profile["keyword_weights"][kw] = max(-15, self.profile["keyword_weights"].get(kw, 0) - 5)

        # 3. Dynamic threshold tuning
        # If user is declining a majority of roles, nudge threshold up to filter noise
        total = self.profile["applied_count"] + self.profile["declined_count"]
        if total >= 3:
            ratio = self.profile["declined_count"] / total
            if ratio > 0.7:
                self.profile["calibrated_threshold"] = min(85, self.profile["calibrated_threshold"] + 1)

        # 4. Audit history
        self.profile["recent_actions"].insert(0, {
            "timestamp": datetime.now().isoformat(),
            "action": "declined",
            "company": company,
            "title": title,
            "reasons": reasons,
            "notes": notes,
        })
        self.profile["recent_actions"] = self.profile["recent_actions"][:25]
        self._save_profile()
        print(f"[LEARNING] Recorded declined role: {company} - {title}. Reasons: {reasons}. Calibrated threshold: {self.profile['calibrated_threshold']}%.")
        return self.get_summary()

    def calculate_learned_adjustment(self, job_data: dict) -> tuple[int, list[str], bool]:
        """Calculate score delta and rationale bullets based on learned candidate preferences."""
        company = str(job_data.get("company", "")).strip()
        
        # Check blocked companies
        for b in self.profile.get("blocked_companies", []):
            if b.lower() == company.lower():
                return (-100, [f"Excluded by learning agent: Blocked company '{company}'"], True)

        delta = 0
        bullets = []

        # Company affinity
        comp_aff = self.profile.get("company_affinity", {}).get(company, 0)
        if comp_aff != 0:
            delta += comp_aff
            sign = "+" if comp_aff > 0 else ""
            bullets.append(f"Company affinity ({sign}{comp_aff}): past feedback on {company}")

        # Keyword weights
        kws = self._extract_job_keywords(job_data)
        kw_delta = 0
        favored_kws = []
        penalized_kws = []

        for kw in kws:
            wt = self.profile.get("keyword_weights", {}).get(kw, 0)
            if wt > 0:
                kw_delta += min(4, wt)
                favored_kws.append(kw.upper())
            elif wt < 0:
                kw_delta += max(-4, wt)
                penalized_kws.append(kw.upper())

        kw_delta = max(-15, min(15, kw_delta))
        delta += kw_delta

        if favored_kws:
            bullets.append(f"Learned preference bonus (+{min(15, kw_delta)}): preferred traits [{', '.join(favored_kws[:3])}]")
        if penalized_kws:
            bullets.append(f"Learned preference penalty ({kw_delta}): downweighted traits [{', '.join(penalized_kws[:3])}]")

        # Clamp overall delta to [-25, +25]
        clamped_delta = max(-25, min(25, delta))
        return (clamped_delta, bullets, False)

    def get_current_threshold(self, is_account_gated: bool = False) -> int:
        """Return the active adaptive threshold."""
        if is_account_gated:
            friction_count = self.profile.get("reason_counts", {}).get("Account creation friction", 0)
            # If user has flagged account friction, raise gate even higher
            return min(98, settings.search.score_threshold_account_gated + (2 if friction_count > 0 else 0))
        return self.profile.get("calibrated_threshold", settings.search.score_threshold_frictionless)

    def get_summary(self) -> dict:
        """Expose summary metrics for API and Dashboard UI."""
        k_weights = self.profile.get("keyword_weights", {})
        top_pos = sorted([k for k, v in k_weights.items() if v > 0], key=lambda k: k_weights[k], reverse=True)[:5]
        top_neg = sorted([k for k, v in k_weights.items() if v < 0], key=lambda k: k_weights[k])[:5]

        return {
            "calibrated_threshold": self.get_current_threshold(is_account_gated=False),
            "applied_count": self.profile.get("applied_count", 0),
            "declined_count": self.profile.get("declined_count", 0),
            "top_preferred_traits": top_pos,
            "top_penalized_traits": top_neg,
            "blocked_companies": self.profile.get("blocked_companies", []),
            "reason_breakdown": self.profile.get("reason_counts", {}),
        }

learning_agent_instance = LearningAgent()
