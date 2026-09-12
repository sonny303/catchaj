"""Helper to render master_resume.md as a clean, styled PDF resume using Playwright."""

import re
import importlib.util
from pathlib import Path
from playwright.sync_api import sync_playwright

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


def md_to_html(md_text: str) -> str:
    """Convert clean resume markdown into semantic HTML without external markdown dependencies."""
    lines = md_text.splitlines()
    body_elements = []
    in_list = False

    for line in lines:
        stripped = line.strip()
        if not stripped:
            if in_list:
                body_elements.append("</ul>")
                in_list = False
            continue

        if stripped.startswith("# "):
            if in_list:
                body_elements.append("</ul>")
                in_list = False
            body_elements.append(f"<h1>{stripped[2:].strip()}</h1>")
        elif stripped.startswith("## "):
            if in_list:
                body_elements.append("</ul>")
                in_list = False
            body_elements.append(f"<h2>{stripped[3:].strip()}</h2>")
        elif stripped.startswith("### "):
            if in_list:
                body_elements.append("</ul>")
                in_list = False
            body_elements.append(f"<h3>{stripped[4:].strip()}</h3>")
        elif stripped.startswith("- ") or stripped.startswith("* "):
            if not in_list:
                body_elements.append("<ul>")
                in_list = True
            item_text = stripped[2:].strip()
            item_text = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", item_text)
            body_elements.append(f"<li>{item_text}</li>")
        else:
            if in_list:
                body_elements.append("</ul>")
                in_list = False
            if len(body_elements) == 1 and body_elements[0].startswith("<h1>"):
                body_elements.append(f'<div class="contact">{stripped}</div>')
            else:
                p_text = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", stripped)
                body_elements.append(f"<p>{p_text}</p>")

    if in_list:
        body_elements.append("</ul>")

    inner_html = "\n    ".join(body_elements)

    return f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<style>
    body {{
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
        line-height: 1.4;
        color: #1a1a1a;
        margin: 40px;
        font-size: 13px;
    }}
    h1 {{
        font-size: 24px;
        margin-bottom: 4px;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }}
    .contact {{
        font-size: 12px;
        color: #444;
        margin-bottom: 16px;
        border-bottom: 1px solid #ccc;
        padding-bottom: 8px;
    }}
    h2 {{
        font-size: 14px;
        text-transform: uppercase;
        border-bottom: 1px solid #222;
        padding-bottom: 2px;
        margin-top: 14px;
        margin-bottom: 8px;
        letter-spacing: 0.5px;
    }}
    h3 {{
        font-size: 13px;
        margin-top: 10px;
        margin-bottom: 2px;
    }}
    p {{
        margin: 4px 0;
    }}
    ul {{
        margin: 4px 0 10px 18px;
        padding: 0;
    }}
    li {{
        margin-bottom: 4px;
    }}
</style>
</head>
<body>
    {inner_html}
</body>
</html>
"""


def generate_pdf_resume(source_doc: Path = None, output_pdf: Path = None):
    truth_doc = source_doc or (settings.truth_doc_path.parent / "master_resume.md")
    pdf_out = output_pdf or (settings.truth_doc_path.parent / "resume.pdf")

    if not truth_doc.exists():
        fallback = settings.truth_doc_path.parent / "career_truth_doc.template.md"
        if fallback.exists():
            print(f"[*] master_resume.md not found. Using template document: {fallback}")
            truth_doc = fallback
        else:
            print(f"[-] Source resume document not found at {truth_doc}")
            return

    content = truth_doc.read_text(encoding="utf-8")
    html_content = md_to_html(content)

    temp_html = settings.truth_doc_path.parent / "resume_temp.html"
    temp_html.write_text(html_content, encoding="utf-8")

    try:
        with sync_playwright() as p:
            browser = p.chromium.launch()
            page = browser.new_page()
            page.goto(f"file://{temp_html.resolve()}")
            page.pdf(path=str(pdf_out), format="A4", margin={"top": "20px", "bottom": "20px", "left": "25px", "right": "25px"})
            browser.close()
        print(f"[✓] Generated base resume PDF at: {pdf_out}")
    except Exception as e:
        print(f"[!] Playwright browser launch failed ({e}). Falling back to native system converter...")
        import subprocess
        try:
            with open(pdf_out, "wb") as f_out:
                subprocess.run(
                    ["cupsfilter", str(truth_doc)],
                    stdout=f_out,
                    stderr=subprocess.DEVNULL,
                    check=True,
                )
            print(f"[✓] Generated base resume PDF via native converter at: {pdf_out}")
        except Exception as e2:
            print(f"[!] Native converter also unavailable ({e2}). PDF output not written.")
    finally:
        temp_html.unlink(missing_ok=True)


if __name__ == "__main__":
    generate_pdf_resume()
