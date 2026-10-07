# Review

A document is ready only after all five gates. Do not skip one because the
earlier ones passed. Report failures to the person plainly; do not hide a
failed check behind a rewrite.

## Gate 1: claims (before rendering)

```sh
python scripts/check.py --content <doc>.content.json --catalog <workspace>/catalog.json
```

It fails a block that cites no evidence, cites an id that does not exist, or
contains a number its evidence does not contain. Fix the content, not the
catalog, unless the person confirms a new fact.

The script cannot read meaning. Check these yourself, block by block against
the cited facts:

- Does the sentence say more than the fact does? ("led" for "worked on",
  "designed" for "implemented", "expert" for a skill they called working level)
- Is an `approximate` fact worded as approximate?
- Does anything break `rules.md`?
- Are employer names, titles and dates exactly as in the catalog?

## Gate 2: render

```sh
python scripts/render.py --content <doc>.content.json \
    --template <workspace>/base/<doc>.docx --style <workspace>/base/<doc>.style.json \
    --out <application folder>/out/<Name>-<Company>-<Doc>
```

## Gate 3: mechanical checks on the output

```sh
python scripts/check.py --content <doc>.content.json --catalog <workspace>/catalog.json \
    --template <workspace>/base/<doc>.docx --style <workspace>/base/<doc>.style.json \
    --docx <out>.docx --pdf <out>.pdf --images <application folder>/out/pages \
    --report <application folder>/out/review.json
```

- **Page count over the limit**: cut content and re-render. Never change fonts,
  sizes, spacing or margins to make it fit.
- **Text missing from the PDF**: something was clipped or dropped. Find it in
  the page image.
- **Fonts substituted**: the converter did not have the template's font, so the
  PDF will not look like the Word file. Tell the person which font is missing
  and how to install it, or have them export the PDF from Word themselves.
  Do not present a substituted PDF as matching their style.

## Gate 4: look at it

Open every page image the check wrote and look, the way the person would:

- Does it look like their base document? Same heading style, spacing, bullets,
  alignment of dates.
- A section heading stranded at the bottom of a page, one line alone on a last
  page, a role split awkwardly across pages.
- Lines that run into each other, a date pushed onto the next line, uneven
  spacing between sections.
- Links present and readable.

If the pages cannot be rendered to images, say so and ask the person to look
before approving. Do not claim a visual review you did not do.

## Gate 5: second reviewer

Hand the job posting, the content file, the catalog and the page images to a
fresh reviewer that did not write the draft (a subagent, or a new session).
Ask it for problems only:

- Claims the evidence does not support, or that overstate it.
- Requirements in the posting that are answered weakly or not at all.
- Wording that sounds generic, inflated or machine-written.
- In the cover letter: wrong company or role name, sentences that could be in
  anyone's letter, anything not in the person's voice.
- Typos, tense changes, inconsistent punctuation or date formats.

Fix what is right, re-run the gates you affected, and tell the person what the
reviewer found, including points you chose not to act on and why. If no second
reviewer is available, say the document had a single review.

## Then the person

Show the documents, the differences from their base, the uncovered
requirements and the review findings. They approve, edit or reject. Only their
approval makes a document final.
