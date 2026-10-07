# File formats

Working examples for a fictional person are in `examples/sample/`.

## settings.json

```json
{"formats": ["docx", "pdf"], "resume_page_limit": 2, "cover_letter_page_limit": 1}
```

`formats` may be `["docx"]`, `["pdf"]` or both. `render.py` reads it from the
nearest `settings.json` above the content file unless `--formats` is given.

## catalog.json

```json
{
  "entries": [
    {
      "id": "northwind-2021",
      "type": "role",
      "title": "Senior Frontend Engineer",
      "org": "Northwind Traders",
      "start": "2021-03",
      "end": "present",
      "location": "Remote",
      "summary": "Leads the web checkout team.",
      "facts": [
        {
          "id": "f1",
          "text": "Rebuilt the checkout flow in React and TypeScript; conversion rose from 2.1% to 2.9% over 6 months.",
          "confidence": "confirmed",
          "source": "interview 2026-10-07; analytics export"
        }
      ]
    }
  ],
  "skills": [
    {"id": "react", "name": "React", "level": "expert", "years": 7, "evidence": ["northwind-2021.f1"]}
  ]
}
```

- `type`: `role`, `project`, `education`, `certification`, `volunteer`, `award`, `other`.
- Ids are short, lowercase and never reused. Do not renumber facts; documents cite them.
- `confidence`: `confirmed`, `approximate` or `unverified`.
- Evidence ids are an entry (`northwind-2021`), a fact (`northwind-2021.f1`) or a skill (`react`).
- Write numbers in facts the way they will be printed (`2.9%`, `35`), because the
  check compares digits. If a document says "four", the check has nothing to compare.

## Content files (`*.content.json`)

```json
{
  "blocks": [
    {"role": "name", "text": "Jane Doe"},
    {"role": "contact", "text": "Austin, TX | jane@example.com | [linkedin.com/in/janedoe](https://www.linkedin.com/in/janedoe)"},
    {"role": "section", "text": "EXPERIENCE"},
    {"role": "entry", "text": "**Northwind Traders** — Senior Frontend Engineer\tMar 2021 – Present", "evidence": ["northwind-2021"]},
    {"role": "bullet", "text": "Rebuilt the checkout flow in React and TypeScript, raising conversion from 2.1% to 2.9% in 6 months.", "evidence": ["northwind-2021.f1"]}
  ]
}
```

One block is one paragraph. `role` must exist in the style map. Inline markup:
`**bold**`, `*italic*`, `[text](url)` and a tab (`\t`, for right-aligned dates
when the template paragraph has a tab stop). Without markup, a block keeps the
template paragraph's own bold and italic.

Blocks need `evidence` unless their role is layout or identity. The default
exempt roles are `name`, `contact`, `section`, `date`, `recipient`, `greeting`,
`closing`, `signature` and `question`.

## Style maps (`*.style.json`)

```json
{
  "template": "resume.docx",
  "roles": {
    "name": {"paragraph": 0},
    "contact": {"paragraph": 1},
    "section": {"paragraph": 2},
    "body": {"paragraph": 3},
    "entry": {"paragraph": 4},
    "bullet": {"paragraph": 5},
    "skills": {"paragraph": 6}
  },
  "contract": {"page_limit": 2, "section_order": ["SUMMARY", "SKILLS", "EXPERIENCE", "EDUCATION"]},
  "no_evidence_roles": ["name", "contact", "section"]
}
```

`paragraph` is the index printed by `inspect_template.py`. Rendering copies
that paragraph for every block with the role and replaces its text, so pick a
paragraph whose formatting is typical for the role. `no_evidence_roles` is
optional and replaces the default list. `section_order` is for you to follow
when drafting; it is not checked by the script.

Only top-level paragraphs can be roles. Text in tables, text boxes and
multi-column sections is not supported.

## requirement-map.json

```json
{
  "job": "Senior Frontend Engineer, Fabrikam",
  "requirements": [
    {"text": "5+ years of React", "status": "supported", "evidence": ["react", "northwind-2021.f1"]},
    {"text": "GraphQL", "status": "adjacent", "evidence": ["contoso-2018.f1"], "note": "REST only; has consumed a GraphQL API, not designed one"},
    {"text": "Team lead experience", "status": "gap"}
  ]
}
```
