"""Web UI Dashboard for Healthcare PM Job Application Engine.

Revamped based on user feedback:
- 2 Clean Views: (1) Jobs to Apply For, (2) Jobs Applied For & Archive
- Intuitive 1-click 'Decline' workflow with structured feedback loop
- Clean non-blocking 'Stage Application' with in-UI submission confirmation
- Removed non-value top clutter cards and irrelevant Q&A popups
- Expandable tailored highlights inline
"""

import os
import json
import threading
import importlib.util
from datetime import datetime
from pathlib import Path
from flask import Flask, jsonify, request, render_template_string, send_from_directory

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
from daemon import daemon_instance
from pipeline_discover import detect_ats_platform, scan_jobs
from pipeline_evaluate import process_and_triage_job
from pipeline_tailor import process_tailoring_pipeline
from run_staged_application import (
    stage_application,
    close_staging_session,
    active_staging_sessions,
)
from learning_agent import learning_agent_instance

FEEDBACK_FILE = settings.truth_doc_path.parent / "user_feedback.json"

STATIC_DIR = Path(__file__).parent / "static"
app = Flask(__name__, static_folder=str(STATIC_DIR))
client = SheetsClient()

DASHBOARD_HTML = r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>catchaj — PM Application Board</title>
<link rel="icon" href="/static/logo.png" type="image/png">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Newsreader:ital,opsz,wght@0,6..72,400;0,6..72,500;0,6..72,600;0,6..72,700;1,6..72,400;1,6..72,500;1,6..72,600;1,6..72,700&family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600;700&display=swap" rel="stylesheet">
<link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css" rel="stylesheet">
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.3/font/bootstrap-icons.min.css">
<style>
    :root {
        --bg-page: #f8fafc;
        --card-bg: #ffffff;
        --border-subtle: #e2e8f0;
        --border-hover: #0055ff;
        --text-primary: #07192f;
        --text-secondary: #334155;
        --text-muted: #64748b;
        --electric-blue: #0055ff;
        --electric-blue-hover: #0043cc;
        --blue-tint: #eff6ff;
        --blue-border: #bfdbfe;
        --navy-dark: #07192f;
        --danger-red: #dc2626;
        --font-serif: 'Newsreader', Georgia, serif;
        --font-sans: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
        --font-mono: 'JetBrains Mono', monospace;
    }
    body {
        background-color: var(--bg-page);
        color: var(--text-secondary);
        font-family: var(--font-sans);
        padding-bottom: 80px;
        -webkit-font-smoothing: antialiased;
        font-size: 14.5px;
        line-height: 1.6;
    }
    h1, h2, h3, h4, h5, h6 {
        color: var(--text-primary);
        font-family: var(--font-sans);
        letter-spacing: -0.02em;
    }
    .header-bar {
        background-color: rgba(255, 255, 255, 0.96);
        backdrop-filter: blur(12px);
        border-bottom: 1px solid var(--border-subtle);
        padding: 14px 32px;
        position: sticky;
        top: 0;
        z-index: 100;
    }
    .brand-logo-wrap {
        display: flex;
        align-items: center;
        gap: 8px;
        text-decoration: none;
    }
    .brand-logo-text {
        font-family: var(--font-sans);
        font-weight: 800;
        font-size: 22px;
        letter-spacing: -0.8px;
        color: var(--navy-dark);
    }
    .badge-hitl {
        font-family: var(--font-mono);
        font-size: 10px;
        font-weight: 700;
        letter-spacing: 0.5px;
        background: var(--blue-tint);
        color: var(--electric-blue);
        border: 1px solid var(--blue-border);
        border-radius: 4px;
        padding: 3px 8px;
    }
    .badge-24h {
        font-family: var(--font-mono);
        font-size: 10px;
        font-weight: 700;
        letter-spacing: 0.5px;
        background: #f1f5f9;
        color: var(--text-primary);
        border: 1px solid var(--border-subtle);
        border-radius: 4px;
        padding: 3px 8px;
    }
    .badge-agent {
        font-family: var(--font-mono);
        font-size: 10px;
        font-weight: 600;
        letter-spacing: 0.3px;
        background: #f0fdf4;
        color: #166534;
        border: 1px solid #bbf7d0;
        border-radius: 4px;
        padding: 3px 8px;
    }

    /* Hero / Board Title Area */
    .board-hero {
        padding: 24px 0 12px 0;
    }
    .eyebrow-tag {
        font-family: var(--font-mono);
        font-size: 11px;
        font-weight: 700;
        color: var(--electric-blue);
        letter-spacing: 1.5px;
        text-transform: uppercase;
        margin-bottom: 8px;
    }
    .board-heading {
        font-family: var(--font-serif);
        font-size: 40px;
        font-weight: 500;
        line-height: 1.15;
        letter-spacing: -1.2px;
        color: var(--navy-dark);
        margin-bottom: 8px;
    }
    .accent-blue-serif {
        color: var(--electric-blue);
        font-style: italic;
        font-weight: 400;
        font-family: var(--font-serif);
    }
    .board-subheading {
        font-size: 15px;
        color: var(--text-muted);
        max-width: 680px;
        line-height: 1.6;
        margin-bottom: 24px;
    }
    .board-subheading strong {
        color: var(--text-primary);
        font-weight: 600;
    }

    /* 3-Column Principles Bar */
    .principles-grid {
        display: grid;
        grid-template-columns: repeat(3, 1fr);
        border: 1px solid var(--border-subtle);
        background: #ffffff;
        border-radius: 8px;
        overflow: hidden;
    }
    .principle-card {
        padding: 16px 20px;
        display: flex;
        gap: 14px;
        align-items: flex-start;
        border-right: 1px solid var(--border-subtle);
    }
    .principle-card:last-child {
        border-right: none;
    }
    .principle-idx {
        font-family: var(--font-mono);
        font-size: 12px;
        font-weight: 700;
        color: var(--electric-blue);
        padding-top: 2px;
    }
    .principle-name {
        font-size: 13.5px;
        font-weight: 700;
        color: var(--text-primary);
        margin-bottom: 2px;
    }
    .principle-desc {
        font-size: 12px;
        color: var(--text-muted);
        line-height: 1.45;
    }

    /* Segmented Control Tabs */
    .shadcn-tabs {
        display: inline-flex;
        background: #f1f5f9;
        border: 1px solid var(--border-subtle);
        border-radius: 8px;
        padding: 4px;
        gap: 4px;
    }
    .shadcn-tab-btn {
        display: inline-flex;
        align-items: center;
        gap: 8px;
        padding: 8px 18px;
        font-size: 13px;
        font-weight: 600;
        color: var(--text-muted);
        border-radius: 6px;
        border: none;
        background: transparent;
        cursor: pointer;
        transition: all 0.15s ease;
    }
    .shadcn-tab-btn:hover {
        color: var(--text-primary);
        background: rgba(255, 255, 255, 0.6);
    }
    .shadcn-tab-btn.active {
        background: var(--navy-dark);
        color: #ffffff;
        box-shadow: 0 1px 3px rgba(7, 25, 47, 0.2);
    }
    .badge-count {
        background: #e2e8f0;
        color: var(--text-primary);
        font-size: 11px;
        font-weight: 700;
        padding: 2px 7px;
        border-radius: 9999px;
    }
    .shadcn-tab-btn.active .badge-count {
        background: var(--electric-blue);
        color: #ffffff;
    }

    /* Job Card */
    .job-card {
        background-color: var(--card-bg);
        border: 1px solid var(--border-subtle);
        border-radius: 10px;
        padding: 22px 24px;
        margin-bottom: 14px;
        transition: all 0.2s cubic-bezier(0.16, 1, 0.3, 1);
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.02), 0 4px 16px rgba(7, 25, 47, 0.03);
    }
    .job-card:hover {
        border-color: var(--electric-blue);
        box-shadow: 0 12px 32px -4px rgba(0, 85, 255, 0.09);
        transform: translateY(-1px);
    }

    /* Circular / Pill Score Badge (matching Screenshot 1) */
    .score-circle {
        width: 54px;
        height: 54px;
        border-radius: 50%;
        border: 2px solid var(--electric-blue);
        background: var(--blue-tint);
        color: var(--electric-blue);
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        flex-shrink: 0;
        transition: transform 0.2s ease;
    }
    .score-circle .score-val {
        font-family: var(--font-serif);
        font-size: 19px;
        font-weight: 700;
        line-height: 1;
    }
    .score-circle .score-unit {
        font-family: var(--font-mono);
        font-size: 8px;
        font-weight: 700;
        letter-spacing: 0.5px;
        opacity: 0.85;
    }
    .score-high {
        border-color: var(--electric-blue);
        background: var(--blue-tint);
        color: var(--electric-blue);
    }
    .score-mid {
        border-color: #2563eb;
        background: #f0f7ff;
        color: #2563eb;
    }
    .score-sub {
        border-color: #94a3b8;
        background: #f8fafc;
        color: #64748b;
    }

    /* Metadata Chips */
    .meta-chip {
        display: inline-flex;
        align-items: center;
        font-size: 12px;
        color: var(--text-muted);
        background: #f8fafc;
        border: 1px solid var(--border-subtle);
        border-radius: 6px;
        padding: 4px 9px;
        line-height: 1;
    }
    .meta-chip.date-chip {
        color: var(--electric-blue);
        background: var(--blue-tint);
        border-color: var(--blue-border);
        font-weight: 600;
    }
    .meta-link {
        display: inline-flex;
        align-items: center;
        font-size: 12px;
        color: var(--electric-blue);
        text-decoration: none;
        padding: 4px 8px;
        border-radius: 6px;
        transition: all 0.15s ease;
        font-weight: 600;
    }
    .meta-link:hover {
        color: var(--electric-blue-hover);
        background: var(--blue-tint);
        text-decoration: underline;
        text-underline-offset: 4px;
    }

    /* Buttons */
    .btn-shadcn-primary {
        background: var(--navy-dark);
        color: #ffffff;
        font-weight: 600;
        font-size: 13px;
        padding: 9px 18px;
        border-radius: 6px;
        border: 1px solid var(--navy-dark);
        display: inline-flex;
        align-items: center;
        gap: 6px;
        transition: all 0.2s ease;
        cursor: pointer;
        line-height: 1;
    }
    .btn-shadcn-primary:hover {
        background: var(--electric-blue);
        border-color: var(--electric-blue);
        color: #ffffff;
        transform: translateY(-1px);
        box-shadow: 0 4px 14px rgba(0, 85, 255, 0.3);
    }
    .btn-shadcn-outline {
        background: #ffffff;
        color: var(--navy-dark);
        font-weight: 600;
        font-size: 13px;
        padding: 8px 15px;
        border-radius: 6px;
        border: 1px solid var(--border-subtle);
        display: inline-flex;
        align-items: center;
        gap: 6px;
        transition: all 0.15s ease;
        cursor: pointer;
        line-height: 1;
        text-decoration: none;
    }
    .btn-shadcn-outline:hover {
        color: var(--electric-blue);
        border-color: var(--blue-border);
        background: var(--blue-tint);
    }
    .btn-shadcn-danger {
        background: #ffffff;
        color: var(--text-muted);
        font-weight: 600;
        font-size: 13px;
        padding: 8px 14px;
        border-radius: 6px;
        border: 1px solid var(--border-subtle);
        display: inline-flex;
        align-items: center;
        gap: 6px;
        transition: all 0.15s ease;
        cursor: pointer;
        line-height: 1;
    }
    .btn-shadcn-danger:hover {
        color: var(--danger-red);
        background: #fef2f2;
        border-color: #fca5a5;
    }

    /* Staging Banner — Terminal Aesthetic (matching Screenshot 2) */
    .staging-banner {
        background: var(--navy-dark);
        border: 1px solid #1e3a5f;
        border-radius: 10px;
        padding: 20px 24px;
        margin-bottom: 24px;
        display: none;
        color: #ffffff;
        box-shadow: 0 10px 30px rgba(7, 25, 47, 0.2);
    }
    .staging-banner .badge-terminal {
        font-family: var(--font-mono);
        font-size: 10px;
        font-weight: 700;
        letter-spacing: 1px;
        background: rgba(0, 85, 255, 0.2);
        color: #60a5fa;
        border: 1px solid rgba(0, 85, 255, 0.4);
        padding: 3px 8px;
        border-radius: 4px;
    }
    .staging-banner .btn-confirm {
        background: var(--electric-blue);
        color: #ffffff;
        font-weight: 600;
        font-size: 13px;
        padding: 9px 18px;
        border-radius: 6px;
        border: 1px solid var(--electric-blue);
        cursor: pointer;
    }
    .staging-banner .btn-confirm:hover {
        background: var(--electric-blue-hover);
    }
    .staging-banner .btn-close-staging {
        background: transparent;
        color: #cbd5e1;
        font-size: 13px;
        padding: 8px 14px;
        border-radius: 6px;
        border: 1px solid #334155;
        cursor: pointer;
    }
    .staging-banner .btn-close-staging:hover {
        color: #ffffff;
        background: rgba(255, 255, 255, 0.05);
    }

    /* Table (View 2) */
    .shadcn-table-wrapper {
        background: var(--card-bg);
        border: 1px solid var(--border-subtle);
        border-radius: 10px;
        overflow: hidden;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.02);
    }
    .shadcn-table {
        width: 100%;
        border-collapse: separate;
        border-spacing: 0;
        margin: 0;
    }
    .shadcn-table thead th {
        background: #f8fafc;
        color: var(--text-muted);
        font-size: 10px;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 1px;
        padding: 14px 16px;
        border-bottom: 1px solid var(--border-subtle);
        font-family: var(--font-mono);
    }
    .shadcn-table tbody td {
        padding: 14px 16px;
        font-size: 13px;
        color: var(--text-secondary);
        border-bottom: 1px solid #f1f5f9;
        vertical-align: middle;
    }
    .shadcn-table tbody tr:hover td {
        background: #f8fafc;
    }

    /* Accordion */
    .accordion-button {
        background-color: #f8fafc !important;
        color: var(--text-primary) !important;
        font-size: 0.85rem;
        font-weight: 600;
        padding: 10px 14px;
        border: 1px solid var(--border-subtle);
        border-radius: 6px !important;
    }
    .accordion-button:not(.collapsed) {
        color: var(--electric-blue) !important;
        border-color: var(--blue-border);
    }
    .accordion-body {
        background-color: #f8fafc;
        border: 1px solid var(--border-subtle);
        border-top: none;
        border-radius: 0 0 6px 6px;
        font-size: 0.9rem;
        white-space: pre-line;
        color: var(--text-secondary);
    }

    /* Modals */
    .modal-content {
        background-color: var(--card-bg);
        border: 1px solid var(--border-subtle);
        border-radius: 10px;
        color: var(--text-primary);
        box-shadow: 0 20px 40px rgba(7, 25, 47, 0.15);
    }
    .modal-header, .modal-footer {
        border-color: var(--border-subtle);
        padding: 16px 20px;
    }
    .form-control, .form-select {
        background-color: #f8fafc;
        border: 1px solid var(--border-subtle);
        color: var(--text-primary);
        border-radius: 6px;
        font-size: 13px;
    }
    .form-control:focus, .form-select:focus {
        background-color: #ffffff;
        color: var(--text-primary);
        border-color: var(--electric-blue);
        box-shadow: 0 0 0 3px rgba(0, 85, 255, 0.12);
    }
    .feedback-tag {
        cursor: pointer;
        display: inline-block;
        padding: 6px 14px;
        margin: 4px;
        border-radius: 20px;
        border: 1px solid var(--border-subtle);
        font-size: 0.82rem;
        background: #f8fafc;
        color: var(--text-muted);
        transition: all 0.15s ease;
    }
    .feedback-tag.selected {
        border-color: #fca5a5;
        background: #fef2f2;
        color: var(--danger-red);
    }

    /* Helpers */
    .font-mono { font-family: var(--font-mono); }
    .font-serif { font-family: var(--font-serif); }
    .text-navy { color: var(--navy-dark) !important; }
    .text-blue { color: var(--electric-blue) !important; }
</style>
</head>
<body>

<!-- TOP NAVIGATION HEADER -->
<div class="header-bar d-flex justify-content-between align-items-center">
    <div class="d-flex align-items-center gap-3">
        <a href="#" class="brand-logo-wrap">
            <img src="/static/logo.png" alt="catchaj" style="height: 34px; width: auto; object-fit: contain; display: block;">
        </a>
        <div class="vr mx-1" style="height: 20px; opacity: 0.2;"></div>
        <div class="d-flex align-items-center gap-2 flex-wrap">
            <span class="badge-hitl">HITL LIVE</span>
            <span class="badge-24h"><i class="bi bi-clock-history me-1 text-primary"></i>LAST 24H ONLY</span>
            <span class="badge-agent" id="learningAgentBadge" title="Dynamically calibrated from applied vs skipped feedback"><i class="bi bi-cpu me-1"></i>Adaptive Threshold: 75%</span>
        </div>
    </div>
    <div class="d-flex align-items-center gap-2">
        <button class="btn-shadcn-outline" onclick="triggerScanNow()">
            <i class="bi bi-arrow-repeat text-primary"></i>Scan 24h Openings
        </button>
        <button class="btn-shadcn-outline" data-bs-toggle="modal" data-bs-target="#intakeModal">
            <i class="bi bi-plus-circle text-primary"></i>Add Job URL
        </button>
        <a href="https://docs.google.com/spreadsheets/d/{{ sheet_id }}/edit" target="_blank" class="btn-shadcn-outline">
            <i class="bi bi-file-earmark-spreadsheet text-success"></i>Google Sheet
        </a>
    </div>
</div>

<div class="container-fluid px-4 px-lg-5 mt-3">

    <!-- HERO SECTION MATCHING PRODUCT MARKETING WEBSITE -->
    <div class="board-hero">
        <div class="eyebrow-tag">A PRODUCT EXPERIMENT IN HUMAN + AI</div>
        <h1 class="board-heading">Your next chapter. <span class="accent-blue-serif">Less of the copy-paste.</span></h1>
        <p class="board-subheading">Job hunting is a full-time job. Catchaj takes on the repetitive search, filtering, drafting, and form-filling. <strong>You make the call.</strong></p>
    </div>

    <!-- 3-COLUMN PRINCIPLES BAR DIRECT FROM DESIGN -->
    <div class="principles-grid mb-4">
        <div class="principle-card">
            <span class="principle-idx">01</span>
            <div>
                <div class="principle-name">Facts over fiction</div>
                <div class="principle-desc">Strict grounding. Zero invented experience.</div>
            </div>
        </div>
        <div class="principle-card">
            <span class="principle-idx">02</span>
            <div>
                <div class="principle-name">Fit over volume</div>
                <div class="principle-desc">High thresholds. Deliberate filters.</div>
            </div>
        </div>
        <div class="principle-card">
            <span class="principle-idx">03</span>
            <div>
                <div class="principle-name">Assistance over autopilot</div>
                <div class="principle-desc">Human judgment at the finish line.</div>
            </div>
        </div>
    </div>

    <!-- ACTIVE STAGING SESSION BANNER -->
    <div id="activeStagingBanner" class="staging-banner">
        <div class="d-flex justify-content-between align-items-center flex-wrap gap-3">
            <div>
                <span class="badge-terminal me-2">LIVE BROWSER STAGED</span>
                <strong id="stagingJobTitle" class="fs-6 text-white">Application Staged in Chrome</strong>
                <div class="small text-white-50 mt-1">Review the pre-filled form in Chrome, complete any CAPTCHA, click Submit, then confirm:</div>
            </div>
            <div class="d-flex align-items-center gap-2">
                <button class="btn-confirm" onclick="confirmSubmit()">
                    <i class="bi bi-check-circle me-1"></i>Confirm Submitted
                </button>
                <button class="btn-close-staging" onclick="cancelStaging()">
                    Close Browser
                </button>
            </div>
        </div>
    </div>

    <!-- SHADCN SEGMENTED VIEW TABS -->
    <div class="d-flex justify-content-between align-items-center mb-4 flex-wrap gap-2">
        <div class="shadcn-tabs">
            <button class="shadcn-tab-btn active" id="tabToApplyBtn" onclick="switchView('toApply')">
                <i class="bi bi-inbox"></i>
                <span>Jobs to Apply For</span>
                <span class="badge-count" id="countToApply">0</span>
            </button>
            <button class="shadcn-tab-btn" id="tabAppliedBtn" onclick="switchView('applied')">
                <i class="bi bi-archive"></i>
                <span>Jobs Applied & History</span>
                <span class="badge-count" id="countApplied">0</span>
            </button>
        </div>
        <div class="small text-muted" id="pipelineStatusInfo">
            Auto-triage active • <span class="text-blue fw-semibold"><i class="bi bi-clock-history me-1"></i>Filtered to past 24h</span> • <span class="text-success fw-semibold" id="learningStatsText"><i class="bi bi-lightning-charge me-1"></i>Learning Agent Active</span> • Seattle onsite or US/Canada Remote
        </div>
    </div>

    <!-- VIEW 1: JOBS TO APPLY FOR -->
    <div id="toApplyView">
        <div id="toApplyContainer">
            <div class="text-center py-5 text-muted">Loading qualified applications...</div>
        </div>
    </div>

    <!-- VIEW 2: JOBS APPLIED FOR & ARCHIVE -->
    <div id="appliedView" style="display: none;">
        <div class="shadcn-table-wrapper">
            <table class="shadcn-table">
                <thead>
                    <tr>
                        <th style="width: 60px;">#</th>
                        <th style="width: 80px;">Score</th>
                        <th>Company</th>
                        <th>Role Title</th>
                        <th>Date Posted</th>
                        <th>Status</th>
                        <th>Audit Log / Timestamp</th>
                        <th class="text-end">Posting</th>
                    </tr>
                </thead>
                <tbody id="appliedTbody">
                    <tr>
                        <td colspan="8" class="text-center py-5 text-muted">No applications in history yet.</td>
                    </tr>
                </tbody>
            </table>
        </div>
    </div>

</div>

<!-- MODAL: DECLINE / FEEDBACK -->
<div class="modal fade" id="declineModal" tabindex="-1">
    <div class="modal-dialog">
        <div class="modal-content">
            <div class="modal-header">
                <h6 class="modal-title fw-bold" style="color: var(--navy-dark);"><i class="bi bi-x-circle text-danger me-2"></i>Decline Role & Give Feedback</h6>
                <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
            </div>
            <div class="modal-body">
                <p class="small text-muted mb-3">Why are you declining this role? The evaluator agent will update candidate preferences to refine future matches.</p>
                <div class="mb-3">
                    <label class="form-label small fw-semibold" style="color: var(--navy-dark);">Select Reasons:</label>
                    <div>
                        <span class="feedback-tag" onclick="toggleTag(this, 'Not interested in company')">Not interested in company</span>
                        <span class="feedback-tag" onclick="toggleTag(this, 'Not healthcare/clinical enough')">Not healthcare/clinical enough</span>
                        <span class="feedback-tag" onclick="toggleTag(this, 'Location/Timezone mismatch')">Location/Timezone mismatch</span>
                        <span class="feedback-tag" onclick="toggleTag(this, 'Role too junior')">Role too junior</span>
                        <span class="feedback-tag" onclick="toggleTag(this, 'Role too senior / executive')">Role too senior / executive</span>
                        <span class="feedback-tag" onclick="toggleTag(this, 'Tech stack mismatch')">Tech stack mismatch</span>
                        <span class="feedback-tag" onclick="toggleTag(this, 'Account creation friction')">Account creation friction</span>
                    </div>
                </div>
                <div class="mb-3">
                    <label class="form-label small fw-semibold" style="color: var(--navy-dark);">Additional Notes (Optional):</label>
                    <textarea id="declineNotes" class="form-control" rows="2" placeholder="e.g. Focus on B2B hospital EHR integrations over patient marketing"></textarea>
                </div>
            </div>
            <div class="modal-footer">
                <button type="button" class="btn-shadcn-outline" data-bs-dismiss="modal">Cancel</button>
                <button type="button" class="btn-shadcn-danger" onclick="submitDecline()">
                    <i class="bi bi-trash"></i>Confirm Decline
                </button>
            </div>
        </div>
    </div>
</div>

<!-- MODAL: INTAKE JOB URL -->
<div class="modal fade" id="intakeModal" tabindex="-1">
    <div class="modal-dialog">
        <div class="modal-content">
            <div class="modal-header">
                <h6 class="modal-title fw-bold" style="color: var(--navy-dark);"><i class="bi bi-link-45deg me-2 text-primary"></i>Intake Job URL</h6>
                <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
            </div>
            <div class="modal-body">
                <div class="mb-3">
                    <label class="form-label small text-muted">Company Name</label>
                    <input type="text" id="intakeCompany" class="form-control" placeholder="e.g. Truveta">
                </div>
                <div class="mb-3">
                    <label class="form-label small text-muted">Job Title</label>
                    <input type="text" id="intakeTitle" class="form-control" placeholder="e.g. Senior Product Manager - Data Interoperability">
                </div>
                <div class="mb-3">
                    <label class="form-label small text-muted">Job Application URL</label>
                    <input type="url" id="intakeUrl" class="form-control" placeholder="https://job-boards.greenhouse.io/...">
                </div>
                <div class="mb-3">
                    <label class="form-label small text-muted">Location</label>
                    <input type="text" id="intakeLoc" class="form-control" value="US-Remote">
                </div>
            </div>
            <div class="modal-footer">
                <button type="button" class="btn-shadcn-outline" data-bs-dismiss="modal">Cancel</button>
                <button type="button" class="btn-shadcn-primary" onclick="submitIntake()">
                    <i class="bi bi-magic me-1"></i>Triage & Intake
                </button>
            </div>
        </div>
    </div>
</div>

<script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/js/bootstrap.bundle.min.js"></script>
<script>
let currentRows = [];
let pendingDeclineRow = null;
let activeStagingRow = null;
let selectedFeedbackTags = [];
let currentTab = 'toApply';

function switchView(tab) {
    currentTab = tab;
    const toApplyView = document.getElementById('toApplyView');
    const appliedView = document.getElementById('appliedView');
    const tabToApplyBtn = document.getElementById('tabToApplyBtn');
    const tabAppliedBtn = document.getElementById('tabAppliedBtn');

    if (tab === 'toApply') {
        toApplyView.style.display = 'block';
        appliedView.style.display = 'none';
        tabToApplyBtn.classList.add('active');
        tabAppliedBtn.classList.remove('active');
    } else {
        toApplyView.style.display = 'none';
        appliedView.style.display = 'block';
        tabToApplyBtn.classList.remove('active');
        tabAppliedBtn.classList.add('active');
    }
}

function isWithin24Hours(rawDate, auditLog) {
    if (!rawDate && !auditLog) return false;
    const now = new Date();
    
    // Check rawDate first
    if (rawDate && rawDate.trim() && rawDate !== "None" && rawDate !== "nan") {
        const s = rawDate.trim().toLowerCase();
        if (s.includes('today') || s.includes('just now') || s.includes('recent')) return true;
        if (s.includes('yesterday')) return true;
        const rel = s.match(/^(\d+)\s*(mo|month|months|w|week|weeks|d|day|days|h|hr|hour|hours|m|min|minute|minutes)/);
        if (rel) {
            const val = parseInt(rel[1]);
            const unit = rel[2];
            if (unit.startsWith('h') || unit.startsWith('min') || unit === 'm') return true;
            if (unit.startsWith('d')) return val <= 1;
            return false;
        }
        const m = s.match(/(\d{4})-(\d{2})-(\d{2})/);
        if (m) {
            const y = parseInt(m[1]), mo = parseInt(m[2]) - 1, d = parseInt(m[3]);
            const postDate = new Date(Date.UTC(y, mo, d));
            const nowUtc = new Date(Date.UTC(now.getUTCFullYear(), now.getUTCMonth(), now.getUTCDate()));
            const diffDays = Math.floor((nowUtc.getTime() - postDate.getTime()) / (1000 * 60 * 60 * 24));
            return diffDays >= -1 && diffDays <= 1;
        }
        return false;
    }
    
    // Fallback to auditLog
    if (auditLog) {
        const m = auditLog.match(/(\d{4})-(\d{2})-(\d{2})/);
        if (m) {
            const y = parseInt(m[1]), mo = parseInt(m[2]) - 1, d = parseInt(m[3]);
            const postDate = new Date(Date.UTC(y, mo, d));
            const nowUtc = new Date(Date.UTC(now.getUTCFullYear(), now.getUTCMonth(), now.getUTCDate()));
            const diffDays = Math.floor((nowUtc.getTime() - postDate.getTime()) / (1000 * 60 * 60 * 24));
            return diffDays >= -1 && diffDays <= 1;
        }
    }
    return false;
}

function formatPostedDate(rawDate, auditLog) {
    if (rawDate && rawDate.trim() && rawDate !== "None" && rawDate !== "nan") {
        try {
            const parts = rawDate.split('-');
            if (parts.length === 3) {
                const year = parseInt(parts[0]);
                const month = parseInt(parts[1]) - 1;
                const day = parseInt(parts[2]);
                const d = new Date(Date.UTC(year, month, day));
                const now = new Date();
                const nowUtc = new Date(Date.UTC(now.getUTCFullYear(), now.getUTCMonth(), now.getUTCDate()));
                const diffDays = Math.floor((nowUtc.getTime() - d.getTime()) / (1000 * 60 * 60 * 24));
                
                if (diffDays <= 0) return "Posted Today (< 24h)";
                if (diffDays === 1) return "Posted Yesterday (< 24h)";
                return `Posted ${rawDate}`;
            }
            return `Posted ${rawDate}`;
        } catch(e) {
            return `Posted ${rawDate}`;
        }
    }
    
    if (auditLog) {
        return "Discovered Today (< 24h)";
    }
    
    return "Recent (< 24h)";
}

async function loadPipeline() {
    try {
        const res = await fetch('/api/pipeline');
        const data = await res.json();
        currentRows = data.rows || [];
        // Strictly filter to last 24h jobs
        currentRows = currentRows.filter(r => isWithin24Hours(r['Date Posted'], r['Audit Log / Timestamp']));
        renderViews(currentRows);
    } catch(err) {
        console.error('Error loading pipeline:', err);
    }

    // Refresh adaptive threshold and learning agent stats
    try {
        const lRes = await fetch('/api/learning/summary');
        const lData = await lRes.json();
        const lBadge = document.getElementById('learningAgentBadge');
        const lStats = document.getElementById('learningStatsText');
        if (lBadge && lData.calibrated_threshold) {
            lBadge.innerHTML = `<i class="bi bi-cpu me-1"></i>Adaptive Threshold: ${lData.calibrated_threshold}%`;
            if (lData.top_preferred_traits && lData.top_preferred_traits.length > 0) {
                lBadge.title = `Top preferred traits: ${lData.top_preferred_traits.join(', ')}`;
            }
        }
        if (lStats && lData.applied_count !== undefined) {
            lStats.innerHTML = `<i class="bi bi-lightning-charge me-1"></i>Learned: ${lData.applied_count} applied, ${lData.declined_count} skipped`;
        }
    } catch(e) {}
}

function renderViews(rows) {
    const toApplyContainer = document.getElementById('toApplyContainer');
    const appliedTbody = document.getElementById('appliedTbody');

    let toApplyCount = 0;
    let appliedCount = 0;

    const toApplyHtml = [];
    const appliedHtml = [];

    rows.forEach((r, idx) => {
        const rowNum = idx + 2;
        const status = (r.Status || 'New').trim();
        const score = parseInt(r['Match Score'] || 0);
        const postedDateStr = formatPostedDate(r['Date Posted'], r['Audit Log / Timestamp']);

        let scoreStyleClass = 'score-sub';
        if (score >= 95) scoreStyleClass = 'score-high';
        else if (score >= 85) scoreStyleClass = 'score-mid';

        const isArchived = (status.toLowerCase() === 'submitted' || status.toLowerCase() === 'declined' || status.toLowerCase() === 'rejected');

        if (!isArchived) {
            toApplyCount++;
            const hasSpecificQA = (r['Drafted Application Q&A'] || '').trim().length > 0;
            toApplyHtml.push(`
                <div class="job-card" id="card-row-${rowNum}">
                    <div class="d-flex justify-content-between align-items-start gap-3 flex-wrap">
                        <div class="d-flex align-items-start gap-3">
                            <div class="score-circle ${scoreStyleClass}" title="Match Score">
                                <span class="score-val">${score}</span>
                                <span class="score-unit">FIT</span>
                            </div>
                            <div>
                                <div class="font-mono text-muted small fw-bold text-uppercase" style="letter-spacing: 0.8px; font-size: 11px;">
                                    ${r.Company || 'Unknown Company'}
                                </div>
                                <h5 class="mb-1 fw-bold text-navy" style="font-size: 17px; letter-spacing: -0.3px; margin-top: 2px;">
                                    ${r['Job Title'] || 'Product Manager'}
                                </h5>
                                <div class="d-flex align-items-center gap-2 flex-wrap mt-2">
                                    <span class="meta-chip date-chip">
                                        <i class="bi bi-calendar3 me-1"></i>${postedDateStr}
                                    </span>
                                    <span class="meta-chip">
                                        <i class="bi bi-geo-alt me-1"></i>${r['Location / Type'] || 'Remote'}
                                    </span>
                                    <span class="meta-chip font-mono">
                                        <i class="bi bi-layers me-1"></i>${r['ATS Platform'] || 'Direct'}
                                    </span>
                                    <a href="${r['Posting URL'] || '#'}" target="_blank" class="meta-link">
                                        View Posting <i class="bi bi-arrow-up-right ms-1"></i>
                                    </a>
                                </div>
                            </div>
                        </div>
                        <div class="d-flex align-items-center gap-2 mt-1">
                            <button class="btn-shadcn-danger" onclick="openDeclineModal(${rowNum}, '${r.Company}')">
                                <i class="bi bi-x-circle"></i>Decline
                            </button>
                            <button class="btn-shadcn-primary" onclick="stageBrowser(${rowNum}, '${r.Company}', '${r['Job Title']}')">
                                <i class="bi bi-browser-chrome"></i>Stage Application
                            </button>
                        </div>
                    </div>

                    ${hasSpecificQA ? `
                    <div class="accordion mt-3" id="accordion-${rowNum}">
                        <div class="accordion-item bg-transparent border-0">
                            <button class="accordion-button collapsed" type="button" data-bs-toggle="collapse" data-bs-target="#collapse-${rowNum}">
                                <i class="bi bi-chat-left-text me-2 text-primary"></i>View Tailored Application Answers & Highlights
                            </button>
                            <div id="collapse-${rowNum}" class="accordion-collapse collapse">
                                <div class="accordion-body">
                                    <div class="mb-3">
                                        <strong class="text-primary d-block mb-1"><i class="bi bi-question-diamond me-1"></i>Tailored Application Answers:</strong>
                                        <div class="p-3 rounded border" style="background:#ffffff; border-color:#e2e8f0; font-family: var(--font-sans); color: var(--text-primary); line-height: 1.6;">${r['Drafted Application Q&A']}</div>
                                    </div>
                                    ${r['Targeted Bullets'] ? `
                                    <div>
                                        <strong class="text-success d-block mb-1"><i class="bi bi-star me-1"></i>Supporting Verified Accomplishments:</strong>
                                        <div class="p-3 rounded border" style="background:#ffffff; border-color:#e2e8f0; font-family: var(--font-sans); color: var(--text-primary); line-height: 1.6;">${r['Targeted Bullets']}</div>
                                    </div>` : ''}
                                </div>
                            </div>
                        </div>
                    </div>` : ''}
                </div>
            `);
        } else {
            appliedCount++;
            appliedHtml.push(`
                <tr>
                    <td class="text-muted font-mono fw-semibold">#${rowNum}</td>
                    <td>
                        <div class="score-circle ${scoreStyleClass}" style="width: 38px; height: 38px;">
                            <span class="score-val" style="font-size: 14px;">${score}</span>
                        </div>
                    </td>
                    <td class="fw-bold text-navy">${r.Company || ''}</td>
                    <td class="text-secondary fw-semibold">${r['Job Title'] || ''}</td>
                    <td><span class="meta-chip date-chip"><i class="bi bi-calendar3 me-1"></i>${postedDateStr}</span></td>
                    <td>
                        <span class="badge ${status.toLowerCase() === 'submitted' ? 'bg-success' : 'bg-secondary'} font-mono">
                            ${status}
                        </span>
                    </td>
                    <td class="small text-muted font-mono">${r['Audit Log / Timestamp'] || ''}</td>
                    <td class="text-end">
                        <a href="${r['Posting URL'] || '#'}" target="_blank" class="btn-shadcn-outline py-1 px-2" title="Open Job Posting">
                            <i class="bi bi-box-arrow-up-right text-primary"></i>
                        </a>
                    </td>
                </tr>
            `);
        }
    });

    document.getElementById('countToApply').innerText = toApplyCount;
    document.getElementById('countApplied').innerText = appliedCount;

    toApplyContainer.innerHTML = toApplyHtml.length ? toApplyHtml.join('') : '<div class="text-center py-5 text-muted fs-6"><i class="bi bi-clock-history d-block fs-3 mb-2 text-primary opacity-75"></i>No jobs posted in the last 24h currently awaiting application.<br><button class="btn btn-sm btn-outline-primary mt-3" onclick="triggerScanNow()"><i class="bi bi-arrow-repeat me-1"></i>Scan 24h Openings Now</button></div>';
    appliedTbody.innerHTML = appliedHtml.length ? appliedHtml.join('') : '<tr><td colspan="8" class="text-center py-5 text-muted">No applications posted in the last 24h in history.</td></tr>';
}

function openDeclineModal(rowNum, company) {
    pendingDeclineRow = rowNum;
    selectedFeedbackTags = [];
    document.querySelectorAll('.feedback-tag').forEach(el => el.classList.remove('selected'));
    document.getElementById('declineNotes').value = '';
    new bootstrap.Modal(document.getElementById('declineModal')).show();
}

function toggleTag(el, tagText) {
    el.classList.toggle('selected');
    if (el.classList.contains('selected')) {
        selectedFeedbackTags.push(tagText);
    } else {
        selectedFeedbackTags = selectedFeedbackTags.filter(t => t !== tagText);
    }
}

async function submitDecline() {
    if (!pendingDeclineRow) return;
    const notes = document.getElementById('declineNotes').value;
    try {
        await fetch('/api/job/decline', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({
                row: pendingDeclineRow,
                reasons: selectedFeedbackTags,
                notes: notes
            })
        });
        bootstrap.Modal.getInstance(document.getElementById('declineModal')).hide();
        loadPipeline();
    } catch(e) {
        alert('Error declining: ' + e);
    }
}

async function stageBrowser(rowNum, company, title) {
    activeStagingRow = rowNum;
    document.getElementById('stagingJobTitle').innerText = `Staged: ${company} — ${title}`;
    document.getElementById('activeStagingBanner').style.display = 'block';

    try {
        const res = await fetch('/api/job/stage', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({row: rowNum})
        });
        const d = await res.json();
        if (!res.ok) alert(d.error || 'Could not launch staging.');
    } catch(e) {
        alert('Error staging: ' + e);
    }
}

async function confirmSubmit() {
    if (!activeStagingRow) return;
    try {
        await fetch('/api/job/confirm_submit', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({row: activeStagingRow})
        });
        document.getElementById('activeStagingBanner').style.display = 'none';
        activeStagingRow = null;
        loadPipeline();
    } catch(e) {
        alert('Error confirming submit: ' + e);
    }
}

async function cancelStaging() {
    if (!activeStagingRow) return;
    try {
        await fetch('/api/job/cancel_stage', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({row: activeStagingRow})
        });
        document.getElementById('activeStagingBanner').style.display = 'none';
        activeStagingRow = null;
    } catch(e) {}
}

async function triggerScanNow() {
    alert('Started market scan in background. Table will refresh shortly.');
    try {
        await fetch('/api/scan/now', {method: 'POST'});
        setTimeout(loadPipeline, 8000);
    } catch(e) {}
}

async function submitIntake() {
    const company = document.getElementById('intakeCompany').value;
    const title = document.getElementById('intakeTitle').value;
    const url = document.getElementById('intakeUrl').value;
    const loc = document.getElementById('intakeLoc').value;

    if (!company || !title || !url) {
        alert('Please provide Company, Title, and Application URL.');
        return;
    }

    try {
        await fetch('/api/job/intake', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({company, title, url, location: loc})
        });
        bootstrap.Modal.getInstance(document.getElementById('intakeModal')).hide();
        loadPipeline();
    } catch(e) {
        alert('Error: ' + e);
    }
}

loadPipeline();
</script>
</body>
</html>
"""

@app.route("/")
def index():
    return render_template_string(
        DASHBOARD_HTML,
        sheet_id=settings.google_sheet_id,
        candidate=settings.candidate,
    )

@app.route("/logo.png")
def logo():
    return send_from_directory(str(STATIC_DIR), "logo.png")

@app.route("/api/pipeline", methods=["GET"])
def get_pipeline():
    client.purge_jobs_older_than(max_hours=24)
    rows = client.get_all_rows(only_last_24h=True)
    return jsonify({"rows": rows})

@app.route("/api/scan/now", methods=["POST"])
def scan_now():
    def run_scan_thread():
        print("[*] Running on-demand manual market scan (past 24h)...")
        discovered = scan_jobs(search_term="Senior Product Manager Healthcare Remote", location="USA", results_wanted=8, hours_old=24)
        qualified = 0
        for j in discovered:
            if process_and_triage_job(j, client):
                qualified += 1
        if qualified > 0:
            process_tailoring_pipeline(client)

    t = threading.Thread(target=run_scan_thread, daemon=True)
    t.start()
    return jsonify({"message": "Market scan started."})

@app.route("/api/job/intake", methods=["POST"])
def job_intake():
    data = request.json or {}
    url = data.get("url", "").strip()
    company = data.get("company", "").strip()
    title = data.get("title", "").strip()
    loc = data.get("location", "US-Remote").strip()

    ats = detect_ats_platform(url)
    date_now = datetime.now().strftime("%Y-%m-%d")
    job_data = {
        "title": title,
        "company": company,
        "location": loc,
        "url": url,
        "ats_platform": ats,
        "description": f"{title} at {company}",
        "date_posted": date_now,
        "is_remote": "remote" in loc.lower() or "remote" in title.lower(),
    }

    passed = process_and_triage_job(job_data, client)
    if passed:
        process_tailoring_pipeline(client)
        return jsonify({"success": True})
    return jsonify({"success": False, "message": "Did not qualify."})

@app.route("/api/job/decline", methods=["POST"])
def job_decline():
    data = request.json or {}
    row_idx = int(data.get("row", 0))
    reasons = data.get("reasons", [])
    notes = data.get("notes", "")

    rows = client.get_all_rows(only_last_24h=False)
    adj_idx = row_idx - 2

    feedback_entry = {
        "timestamp": datetime.now().isoformat(),
        "row": row_idx,
        "reasons": reasons,
        "notes": notes,
    }

    if 0 <= adj_idx < len(rows):
        job = rows[adj_idx]
        feedback_entry["company"] = job.get("Company")
        feedback_entry["title"] = job.get("Job Title")
        feedback_entry["url"] = job.get("Posting URL")

        # Record with autonomous Learning Agent
        learning_agent_instance.record_declined(job, reasons, notes)

        # Save to persistent feedback store
        existing_feedback = []
        if FEEDBACK_FILE.exists():
            try:
                existing_feedback = json.loads(FEEDBACK_FILE.read_text(encoding="utf-8"))
            except Exception:
                existing_feedback = []
        existing_feedback.append(feedback_entry)
        FEEDBACK_FILE.write_text(json.dumps(existing_feedback, indent=2), encoding="utf-8")

        # Update status in pipeline
        reason_str = ", ".join(reasons)
        client.update_row_status(row_idx, status="Declined")
        print(f"[✓] Row #{row_idx} declined with feedback: {reason_str}")
        return jsonify({"success": True, "learning_summary": learning_agent_instance.get_summary()})

    return jsonify({"error": "Row not found"}), 404

@app.route("/api/job/stage", methods=["POST"])
def job_stage():
    data = request.json or {}
    row_idx = int(data.get("row", 0))
    rows = client.get_all_rows(only_last_24h=False)
    adj_idx = row_idx - 2

    if 0 <= adj_idx < len(rows):
        row_data = rows[adj_idx]

        def run_stage_thread():
            stage_application(row_data, row_idx, client, is_interactive_cli=False)

        t = threading.Thread(target=run_stage_thread, daemon=True)
        t.start()
        return jsonify({"success": True, "message": f"Staging started for {row_data.get('Company')}!"})

    return jsonify({"error": "Row not found"}), 404

@app.route("/api/job/confirm_submit", methods=["POST"])
def job_confirm_submit():
    data = request.json or {}
    row_idx = int(data.get("row", 0))
    rows = client.get_all_rows(only_last_24h=False)
    adj_idx = row_idx - 2

    if 0 <= adj_idx < len(rows):
        job = rows[adj_idx]
        # Record with autonomous Learning Agent (positive reinforcement)
        learning_agent_instance.record_applied(job)

    close_staging_session(row_idx, mark_submitted=True, sheets_client=client)
    return jsonify({"success": True, "learning_summary": learning_agent_instance.get_summary()})

@app.route("/api/job/cancel_stage", methods=["POST"])
def job_cancel_stage():
    data = request.json or {}
    row_idx = int(data.get("row", 0))
    close_staging_session(row_idx, mark_submitted=False, sheets_client=client)
    return jsonify({"success": True})

@app.route("/api/learning/summary", methods=["GET"])
def learning_summary():
    return jsonify(learning_agent_instance.get_summary())

if __name__ == "__main__":
    port = int(os.getenv("PORT", 5001))
    print(f"================================================================")
    print(f" HEALTHCARE PM JOB APPLICATION ENGINE — REVAMPED DASHBOARD")
    print(f" Running at: http://127.0.0.1:{port}")
    print(f"================================================================")
    app.run(host="127.0.0.1", port=port, debug=False)
