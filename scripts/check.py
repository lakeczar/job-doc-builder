#!/usr/bin/env python3
"""Mechanical review of a drafted or rendered document. Exits 1 on any FAIL.

  # claims only (before rendering, or for application answers)
  python check.py --content resume.content.json --catalog catalog.json

  # full check after rendering
  python check.py --content resume.content.json --catalog catalog.json \
      --template base/resume.docx --style base/resume.style.json \
      --docx out/Resume.docx --pdf out/Resume.pdf --images out/pages --report out/review.json

What it checks:
  claims   every content block cites catalog evidence that exists, and every
           number in the block appears in that evidence
  style    page size, margins and fonts of the Word file match the template
  pdf      page count is within the limit, every block's text is present and in
           order (catches clipped or dropped text), and which fonts were embedded
  images   one PNG per page for the agent to look at (needs PyMuPDF)

These checks cannot judge wording, relevance or how the page looks. The agent
and the person still review those.
"""
import argparse
import json
import re
import sys
import unicodedata
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from docx_engine import fonts_used, load_json, page_geometry, plain_text  # noqa: E402

# Roles that are layout or identity, not claims about the person.
NO_EVIDENCE_ROLES = {"name", "contact", "section", "date", "recipient", "greeting", "closing", "signature", "question"}
NUMBER = re.compile(r"\d[\d,]*(?:\.\d+)?")

results = []


def record(level, check, detail):
    results.append({"level": level, "check": check, "detail": detail})
    print(f"{level:<4} {check}: {detail}")


def evidence_index(catalog):
    """Map every citable id to the text that backs it."""
    index = {}
    for entry in catalog.get("entries", []):
        header = " ".join(str(entry.get(k, "")) for k in ("title", "org", "start", "end", "location", "summary"))
        facts = entry.get("facts", [])
        index[entry["id"]] = {"text": header + " " + " ".join(f.get("text", "") for f in facts), "confidence": "confirmed"}
        for fact in facts:
            index[f'{entry["id"]}.{fact["id"]}'] = {
                "text": header + " " + fact.get("text", ""),
                "confidence": fact.get("confidence", "confirmed"),
            }
    for skill in catalog.get("skills", []):
        index[skill["id"]] = {
            "text": " ".join(str(skill.get(k, "")) for k in ("name", "level", "years", "notes")),
            "confidence": "confirmed",
        }
    return index


def check_claims(blocks, catalog, exempt):
    index = evidence_index(catalog)
    problems = 0
    for n, block in enumerate(blocks):
        if block["role"] in exempt:
            continue
        text = plain_text(block.get("text", ""))
        label = f'block {n} ({block["role"]}): "{text[:60]}"'
        cited = block.get("evidence") or []
        if not cited:
            record("FAIL", "claims", f"{label} cites no evidence")
            problems += 1
            continue
        missing = [c for c in cited if c not in index]
        if missing:
            record("FAIL", "claims", f"{label} cites ids not in the catalog: {', '.join(missing)}")
            problems += 1
            continue
        backing = " ".join(index[c]["text"] for c in cited).replace(",", "")
        loose = [n_ for n_ in NUMBER.findall(text) if n_.replace(",", "") not in backing]
        if loose:
            record("FAIL", "claims", f"{label} has numbers not found in its evidence: {', '.join(loose)}")
            problems += 1
        weak = [c for c in cited if index[c]["confidence"] == "unverified"]
        if weak:
            record("WARN", "claims", f"{label} relies on unverified facts: {', '.join(weak)}")
    if not problems:
        record("PASS", "claims", "every claim block cites existing evidence and its numbers are backed")


def check_style(template, docx_path):
    from docx import Document
    base, out = Document(str(template)), Document(str(docx_path))
    if page_geometry(base) == page_geometry(out):
        record("PASS", "style", "page size and margins match the template")
    else:
        record("FAIL", "style", "page size or margins differ from the template")
    extra = fonts_used(out) - fonts_used(base)
    if extra:
        record("FAIL", "style", f"fonts not in the template: {', '.join(sorted(extra))}")
    else:
        record("PASS", "style", "no fonts beyond the template's")
    return fonts_used(base)


def squash(text):
    return re.sub(r"\s+", "", unicodedata.normalize("NFKC", text))


def check_pdf(pdf_path, blocks, page_limit, template_fonts):
    from pypdf import PdfReader
    reader = PdfReader(str(pdf_path))
    pages = len(reader.pages)
    if page_limit and pages > page_limit:
        record("FAIL", "pdf", f"{pages} pages, limit is {page_limit}")
    else:
        record("PASS", "pdf", f"{pages} page(s)" + (f", limit {page_limit}" if page_limit else ""))

    text = squash("".join(page.extract_text() or "" for page in reader.pages))
    position, lost, moved = 0, [], []
    for n, block in enumerate(blocks):
        want = squash(plain_text(block.get("text", "")))
        if not want:
            continue
        found = text.find(want, position)
        if found >= 0:
            position = found + len(want)
        elif want in text:
            moved.append(n)
        else:
            lost.append(f'block {n}: "{plain_text(block["text"])[:50]}"')
    if lost:
        record("FAIL", "pdf", "text missing from the PDF (clipped, dropped or garbled): " + "; ".join(lost[:8]))
    else:
        record("PASS", "pdf", "every block's text is in the PDF")
    if moved:
        record("WARN", "pdf", f"blocks out of reading order: {moved[:12]}")

    embedded = set()
    for page in reader.pages:
        fonts = (page.get("/Resources") or {}).get("/Font") or {}
        for ref in fonts.values():
            name = str(ref.get_object().get("/BaseFont", "")).lstrip("/")
            embedded.add(name.split("+")[-1])
    record("INFO", "pdf", "fonts in the PDF: " + (", ".join(sorted(embedded)) or "none reported"))
    flat = "".join(embedded).replace(" ", "").lower()
    swapped = [f for f in sorted(template_fonts) if f.replace(" ", "").lower() not in flat]
    if template_fonts and swapped and embedded:
        record("WARN", "pdf", f"template fonts not found in the PDF, likely substituted: {', '.join(swapped)}")


def page_images(pdf_path, folder):
    try:
        import pymupdf as fitz
    except ImportError:
        record("WARN", "images", "PyMuPDF not installed; no page images. Open the PDF to look at it.")
        return
    folder = Path(folder)
    folder.mkdir(parents=True, exist_ok=True)
    paths = []
    with fitz.open(str(pdf_path)) as pdf:
        for number, page in enumerate(pdf, 1):
            target = folder / f"page-{number}.png"
            page.get_pixmap(dpi=110).save(str(target))
            paths.append(str(target))
    record("INFO", "images", "look at these before approving: " + ", ".join(paths))


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--content", required=True)
    ap.add_argument("--catalog", required=True)
    ap.add_argument("--template")
    ap.add_argument("--style")
    ap.add_argument("--docx")
    ap.add_argument("--pdf")
    ap.add_argument("--page-limit", type=int)
    ap.add_argument("--images", help="folder for one PNG per PDF page")
    ap.add_argument("--report", help="write the results as JSON")
    args = ap.parse_args()

    blocks = load_json(args.content)["blocks"]
    style = load_json(args.style) if args.style else {}
    exempt = set(style.get("no_evidence_roles", NO_EVIDENCE_ROLES))

    check_claims(blocks, load_json(args.catalog), exempt)
    template_fonts = set()
    if args.docx and args.template:
        template_fonts = check_style(args.template, args.docx)
    if args.pdf:
        limit = args.page_limit or style.get("contract", {}).get("page_limit")
        check_pdf(args.pdf, blocks, limit, template_fonts)
        if args.images:
            page_images(args.pdf, args.images)

    failed = sum(r["level"] == "FAIL" for r in results)
    if args.report:
        Path(args.report).parent.mkdir(parents=True, exist_ok=True)
        Path(args.report).write_text(json.dumps({"failed": failed, "results": results}, indent=2), encoding="utf-8")
    print(f"\n{failed} failure(s)")
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()
