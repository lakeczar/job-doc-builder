"""Shared helpers: fill a person's own Word template with new content.

The approach is exemplar cloning. A style map names one paragraph in the
template for each role (name, section heading, bullet, ...). Rendering copies
that paragraph, formatting and all, once per content block and replaces only
the text. Nothing is restyled, so the output looks like the template.
"""
from __future__ import annotations

import copy
import json
import re
from pathlib import Path

from docx import Document
from docx.opc.constants import RELATIONSHIP_TYPE as RT
from docx.oxml import OxmlElement
from docx.oxml.ns import qn

# **bold**, *italic*, [text](url) and tabs are the only inline markup.
_TOKEN = re.compile(r"(\*\*.+?\*\*|\*.+?\*|\[[^\]]+\]\([^)]+\)|\t)")
_LINK = re.compile(r"\[([^\]]+)\]\(([^)]+)\)")


def load_json(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def plain_text(text: str) -> str:
    """Block text with the inline markup removed, as it should read on the page."""
    text = _LINK.sub(r"\1", text)
    text = re.sub(r"\*\*(.+?)\*\*", r"\1", text)
    text = re.sub(r"\*(.+?)\*", r"\1", text)
    return text.replace("\t", " ")


def body_paragraphs(doc):
    """Top-level body paragraphs, in order. Table and text-box content is not included."""
    return [el for el in doc.element.body if el.tag == qn("w:p")]


def paragraph_text(p) -> str:
    return "".join(t.text or "" for t in p.iter(qn("w:t")))


def _base_rpr(p):
    """Run formatting of the first run that carries text, or None."""
    for r in p.iter(qn("w:r")):
        if any(t.text for t in r.iter(qn("w:t"))):
            rpr = r.find(qn("w:rPr"))
            return copy.deepcopy(rpr) if rpr is not None else None
    return None


def _toggle(rpr, tag: str, on: bool):
    rpr = copy.deepcopy(rpr) if rpr is not None else OxmlElement("w:rPr")
    for name in (tag, tag + "Cs"):
        for el in rpr.findall(qn(name)):
            rpr.remove(el)
    if on:
        rpr.insert(0, OxmlElement(tag))
    return rpr


def _run(rpr, text=None, tab=False):
    r = OxmlElement("w:r")
    if rpr is not None and len(rpr):
        r.append(copy.deepcopy(rpr))
    if tab:
        r.append(OxmlElement("w:tab"))
    else:
        t = OxmlElement("w:t")
        t.text = text
        t.set(qn("xml:space"), "preserve")
        r.append(t)
    return r


def set_paragraph_text(p, text: str, part):
    """Replace the paragraph's runs with `text`, keeping paragraph formatting and
    the formatting of its first text run. Inline markup is applied on top."""
    base = _base_rpr(p)
    for child in list(p):
        if child.tag != qn("w:pPr"):
            p.remove(child)

    # Markup switches bold/italic explicitly; without markup the exemplar's own
    # run formatting is kept untouched (a bold heading stays bold).
    has_bold = "**" in text
    has_italic = bool(re.search(r"(?<!\*)\*(?!\*)", text))

    def fmt(bold=False, italic=False):
        rpr = base
        if has_bold:
            rpr = _toggle(rpr, "w:b", bold)
        if has_italic:
            rpr = _toggle(rpr, "w:i", italic)
        return rpr

    for token in (t for t in _TOKEN.split(text) if t):
        if token == "\t":
            p.append(_run(fmt(), tab=True))
        elif token.startswith("**") and token.endswith("**") and len(token) > 4:
            p.append(_run(fmt(bold=True), token[2:-2]))
        elif token.startswith("*") and token.endswith("*") and len(token) > 2:
            p.append(_run(fmt(italic=True), token[1:-1]))
        elif _LINK.fullmatch(token):
            label, url = _LINK.fullmatch(token).groups()
            link = OxmlElement("w:hyperlink")
            link.set(qn("r:id"), part.relate_to(url, RT.HYPERLINK, is_external=True))
            link.append(_run(fmt(), label))
            p.append(link)
        else:
            p.append(_run(fmt(), token))


def render_docx(template, style_map: dict, blocks: list, out_path):
    """Write a new .docx built from `template` with one cloned paragraph per block."""
    doc = Document(str(template))
    body = doc.element.body
    paragraphs = body_paragraphs(doc)

    exemplars = {}
    for role, spec in style_map["roles"].items():
        index = spec["paragraph"]
        if not 0 <= index < len(paragraphs):
            raise ValueError(f"style map role '{role}' points at paragraph {index}, template has {len(paragraphs)}")
        clone = copy.deepcopy(paragraphs[index])
        # A page or section break belongs to the old layout, not to the role.
        for br in list(clone.iter(qn("w:br"))):
            if br.get(qn("w:type")) == "page":
                br.getparent().remove(br)
        for tag in ("w:lastRenderedPageBreak", "w:sectPr"):
            for el in list(clone.iter(qn(tag))):
                el.getparent().remove(el)
        exemplars[role] = clone

    unknown = sorted({b["role"] for b in blocks} - set(exemplars))
    if unknown:
        raise ValueError(f"content uses roles the style map does not define: {', '.join(unknown)}")

    final_sect = body.find(qn("w:sectPr"))
    for child in list(body):
        if child is not final_sect:
            body.remove(child)
    for block in blocks:
        p = copy.deepcopy(exemplars[block["role"]])
        set_paragraph_text(p, block.get("text", ""), doc.part)
        if final_sect is not None:
            final_sect.addprevious(p)
        else:
            body.append(p)

    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    doc.save(str(out_path))
    return out_path


def fonts_used(doc) -> set:
    """Fonts the document actually uses: set on body runs, in the document
    defaults, or in a style that some body paragraph or run refers to."""
    body, styles = doc.element.body, doc.styles.element
    used = {el.get(qn("w:val")) for tag in ("w:pStyle", "w:rStyle") for el in body.iter(qn(tag))}
    roots = [body] + list(styles.iter(qn("w:docDefaults")))
    for style in styles.iter(qn("w:style")):
        if style.get(qn("w:styleId")) in used or style.get(qn("w:default")) == "1":
            roots.append(style)
    names = set()
    for root in roots:
        for rfonts in root.iter(qn("w:rFonts")):
            for attr in ("w:ascii", "w:hAnsi"):
                value = rfonts.get(qn(attr))
                if value:
                    names.add(value)
    return names


def page_geometry(doc) -> list:
    return [
        tuple(getattr(s, a) for a in ("page_width", "page_height", "left_margin", "right_margin", "top_margin", "bottom_margin"))
        for s in doc.sections
    ]
