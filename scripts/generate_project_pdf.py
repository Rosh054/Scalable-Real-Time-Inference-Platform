#!/usr/bin/env python3
"""Generate formal project PDF from markdown documentation."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DEFAULT_SOURCE = ROOT / "docs" / "PROJECT_FULL_DOCUMENT.md"
DEFAULT_OUTPUT = ROOT / "docs" / "Scalable_Real-Time_Inference_Platform_Formal_Document.pdf"


def _basic_css() -> str:
    return """
    @page { size: A4; margin: 2cm; }
    body {
        font-family: Helvetica, Arial, sans-serif;
        font-size: 11pt;
        line-height: 1.45;
        color: #1a1a1a;
    }
    h1 { font-size: 20pt; color: #0f172a; border-bottom: 2px solid #2563eb; padding-bottom: 6px; }
    h2 { font-size: 14pt; color: #1e3a5f; margin-top: 18px; }
    h3 { font-size: 12pt; color: #334155; }
    table { border-collapse: collapse; width: 100%; margin: 12px 0; }
    th, td { border: 1px solid #cbd5e1; padding: 8px; text-align: left; }
    th { background: #f1f5f9; }
    code, pre { font-family: Menlo, monospace; font-size: 9pt; background: #f8fafc; }
    pre { padding: 10px; border: 1px solid #e2e8f0; white-space: pre-wrap; }
    blockquote { border-left: 4px solid #2563eb; margin-left: 0; padding-left: 12px; color: #475569; }
    hr { border: none; border-top: 1px solid #e2e8f0; margin: 24px 0; }
    """


def generate_with_weasyprint(md_path: Path, pdf_path: Path) -> None:
    import markdown
    from weasyprint import HTML

    md_text = md_path.read_text(encoding="utf-8")
    html_body = markdown.markdown(md_text, extensions=["tables", "fenced_code", "nl2br"])
    html_doc = f"""<!DOCTYPE html>
<html><head><meta charset="utf-8"><style>{_basic_css()}</style></head>
<body>{html_body}</body></html>"""
    HTML(string=html_doc, base_url=str(md_path.parent)).write_pdf(str(pdf_path))


def generate_with_fpdf(md_path: Path, pdf_path: Path) -> None:
    """Fallback: plain-text PDF without rich markdown rendering."""
    from fpdf import FPDF
    from fpdf.enums import XPos, YPos

    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    width = pdf.epw

    def write_line(text: str, h: float = 5, bold: bool = False, size: int = 10) -> None:
        style = "B" if bold else ""
        pdf.set_font("Helvetica", style=style, size=size)
        pdf.set_x(pdf.l_margin)
        safe = text.encode("latin-1", errors="replace").decode("latin-1").strip() or " "
        if len(safe) > 200:
            safe = safe[:197] + "..."
        pdf.multi_cell(width, h, safe, new_x=XPos.LMARGIN, new_y=YPos.NEXT)

    in_code = False
    for raw in md_path.read_text(encoding="utf-8").splitlines():
        line = raw.rstrip()
        if line.startswith("```"):
            in_code = not in_code
            continue
        if in_code:
            write_line(line, h=4, size=8)
            continue
        if line.startswith("# "):
            write_line(line[2:], h=8, bold=True, size=14)
        elif line.startswith("## "):
            write_line(line[3:], h=7, bold=True, size=12)
        elif line.startswith("### "):
            write_line(line[4:], h=6, bold=True, size=11)
        elif line.strip() == "---":
            pdf.ln(3)
        elif line.startswith("|") and "|" in line[1:]:
            write_line(line.replace("|", "  "), h=5, size=9)
        else:
            write_line(line, h=5, size=10)

    pdf.output(str(pdf_path))


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate formal project PDF")
    parser.add_argument("--input", type=Path, default=DEFAULT_SOURCE)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()

    if not args.input.exists():
        print(f"ERROR: Source not found: {args.input}", file=sys.stderr)
        return 1

    args.output.parent.mkdir(parents=True, exist_ok=True)

    engine = None
    for name, fn in (
        ("weasyprint", generate_with_weasyprint),
        ("fpdf", generate_with_fpdf),
    ):
        try:
            fn(args.input, args.output)
            engine = name
            break
        except ImportError:
            continue
        except OSError as exc:
            print(f"Note: {name} unavailable ({exc}); trying fallback...", file=sys.stderr)
            continue

    if engine is None:
        print(
            "Install PDF dependencies:\n"
            "  pip install fpdf2\n"
            "Optional quality: brew install pango && pip install markdown weasyprint",
            file=sys.stderr,
        )
        return 1

    print(f"PDF created ({engine}): {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
