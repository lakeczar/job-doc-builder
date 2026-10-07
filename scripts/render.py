#!/usr/bin/env python3
"""Render a content file into Word and PDF using the person's template.

  python render.py --content resume.content.json --template base/resume.docx \
      --style base/resume.style.json --out out/Jane-Doe-Resume [--formats docx,pdf]

Formats default to the workspace setting, or docx,pdf. PDF conversion uses
LibreOffice when it is installed, otherwise Microsoft Word on Windows.
"""
import argparse
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from docx_engine import load_json, render_docx  # noqa: E402


def find_soffice():
    for name in ("soffice", "libreoffice"):
        found = shutil.which(name)
        if found:
            return found
    for candidate in (
        "/Applications/LibreOffice.app/Contents/MacOS/soffice",
        r"C:\Program Files\LibreOffice\program\soffice.exe",
        r"C:\Program Files (x86)\LibreOffice\program\soffice.exe",
    ):
        if Path(candidate).exists():
            return candidate
    return None


def docx_to_pdf(docx: Path, pdf: Path) -> str:
    """Convert and return the name of the converter used."""
    docx, pdf = docx.resolve(), pdf.resolve()
    soffice = find_soffice()
    if soffice:
        # A throwaway profile keeps this from touching or waiting on a desktop session.
        with tempfile.TemporaryDirectory() as profile:
            subprocess.run(
                [soffice, f"-env:UserInstallation={Path(profile).as_uri()}", "--headless",
                 "--convert-to", "pdf", "--outdir", str(pdf.parent), str(docx)],
                check=True, capture_output=True, timeout=180,
            )
        produced = pdf.parent / (docx.stem + ".pdf")
        if produced != pdf:
            produced.replace(pdf)
        return "libreoffice"
    if os.name == "nt":
        script = (
            "$w = New-Object -ComObject Word.Application; $w.Visible = $false; "
            "try { $d = $w.Documents.Open($env:JDB_DOCX, $false, $true); "
            "$d.SaveAs2($env:JDB_PDF, 17); $d.Close($false) } finally { $w.Quit() }"
        )
        env = dict(os.environ, JDB_DOCX=str(docx), JDB_PDF=str(pdf))
        subprocess.run(["powershell", "-NoProfile", "-NonInteractive", "-Command", script],
                       check=True, capture_output=True, timeout=180, env=env)
        return "word"
    raise RuntimeError("No PDF converter found. Install LibreOffice, or set formats to docx only.")


def workspace_formats(start: Path):
    for folder in [start, *start.parents]:
        settings = folder / "settings.json"
        if settings.exists():
            return load_json(settings).get("formats")
    return None


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--content", required=True)
    ap.add_argument("--template", required=True)
    ap.add_argument("--style", required=True)
    ap.add_argument("--out", required=True, help="output path without extension")
    ap.add_argument("--formats", help="docx, pdf or docx,pdf")
    args = ap.parse_args()

    out = Path(args.out)
    formats = args.formats.split(",") if args.formats else (workspace_formats(Path(args.content).resolve().parent) or ["docx", "pdf"])
    formats = [f.strip().lower() for f in formats]
    if not set(formats) <= {"docx", "pdf"} or not formats:
        sys.exit("formats must be docx, pdf or docx,pdf")

    content, style = load_json(args.content), load_json(args.style)
    # The Word file is always built: it is the source for the PDF.
    keep_docx = "docx" in formats
    docx_path = out.with_suffix(".docx") if keep_docx else Path(tempfile.mkdtemp()) / (out.name + ".docx")
    render_docx(args.template, style, content["blocks"], docx_path)
    if keep_docx:
        print(f"wrote {docx_path}")
    if "pdf" in formats:
        pdf_path = out.with_suffix(".pdf")
        used = docx_to_pdf(docx_path, pdf_path)
        print(f"wrote {pdf_path} (via {used})")
        if used == "libreoffice":
            print("note: LibreOffice substitutes fonts it does not have; run check.py to see the fonts in the PDF.")


if __name__ == "__main__":
    main()
