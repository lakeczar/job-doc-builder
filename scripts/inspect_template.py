#!/usr/bin/env python3
"""List the paragraphs of a Word file so each one can be given a role.

  python inspect_template.py resume.docx
  python inspect_template.py resume.docx --json

Prints index, style, font, size, alignment and the text of every top-level
paragraph, then warns about layout this tool cannot fill (tables, text boxes,
columns). The agent uses the indexes to write the style map.
"""
import argparse
import json
import sys
from pathlib import Path

from docx import Document
from docx.oxml.ns import qn

sys.path.insert(0, str(Path(__file__).parent))
from docx_engine import body_paragraphs, fonts_used, paragraph_text  # noqa: E402


def describe(doc):
    rows = []
    for index, p in enumerate(body_paragraphs(doc)):
        ppr = p.find(qn("w:pPr"))
        style = align = None
        bullet = False
        if ppr is not None:
            s = ppr.find(qn("w:pStyle"))
            style = s.get(qn("w:val")) if s is not None else None
            j = ppr.find(qn("w:jc"))
            align = j.get(qn("w:val")) if j is not None else None
            bullet = ppr.find(qn("w:numPr")) is not None
        font = size = None
        bold = False
        for r in p.iter(qn("w:r")):
            rpr = r.find(qn("w:rPr"))
            if rpr is None:
                continue
            f = rpr.find(qn("w:rFonts"))
            z = rpr.find(qn("w:sz"))
            font = font or (f.get(qn("w:ascii")) if f is not None else None)
            size = size or (int(z.get(qn("w:val"))) / 2 if z is not None else None)
            b = rpr.find(qn("w:b"))
            bold = bold or (b is not None and b.get(qn("w:val")) not in ("0", "false"))
        rows.append({
            "paragraph": index, "style": style, "font": font, "size": size, "bold": bold,
            "align": align, "list": bullet, "tab": bool(list(p.iter(qn("w:tab")))),
            "text": paragraph_text(p),
        })
    return rows


def warnings(doc):
    body = doc.element.body
    out = []
    tables = [el for el in body if el.tag == qn("w:tbl")]
    if tables:
        out.append(f"{len(tables)} table(s): text inside tables is not filled. Rebuild on a starter template or flatten the layout.")
    if list(body.iter(qn("w:txbxContent"))):
        out.append("Text boxes found: their text is not filled.")
    for cols in body.iter(qn("w:cols")):
        if int(cols.get(qn("w:num")) or 1) > 1:
            out.append("Multi-column section found: column layouts are not supported.")
            break
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("docx")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    doc = Document(args.docx)
    rows, warn = describe(doc), warnings(doc)
    if args.json:
        print(json.dumps({"paragraphs": rows, "fonts": sorted(fonts_used(doc)), "warnings": warn}, indent=2))
        return
    for r in rows:
        flags = "".join([" bold" if r["bold"] else "", " list" if r["list"] else "", " tab" if r["tab"] else ""])
        print(f'{r["paragraph"]:>3}  [{r["style"] or "-"} | {r["font"] or "-"} {r["size"] or "-"} | {r["align"] or "left"}{flags}]  {r["text"][:90]}')
    print("\nFonts:", ", ".join(sorted(fonts_used(doc))) or "(theme defaults)")
    for w in warn:
        print("WARNING:", w)


if __name__ == "__main__":
    main()
