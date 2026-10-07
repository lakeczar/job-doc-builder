# Job Doc Builder

A skill for AI coding agents (Claude Code, Codex, Hermes and others that read
`SKILL.md`) that builds a tailored resume, cover letter and application answers
for a specific job, from your own documented experience, in your own Word
style. Output is Word and PDF.

It is built around three rules:

- **Nothing is invented.** Every claim cites an entry in your experience catalog.
- **Your style is kept.** Documents are made by filling your own Word template.
- **You approve.** Nothing is final, and nothing is sent, without you.

It does not search for jobs, rank them or submit applications.

## How it works

1. **Setup wizard, once.** The agent takes your existing resume and cover
   letter or helps you write them, interviews you to build a catalog of
   experience and skills (including what is not on your resume), records your
   rules and writing voice, and learns your document style.
2. **Per job.** Give the agent a job link, a description or application
   questions. It maps the requirements to your catalog, asks you about the
   gaps, drafts, reviews and renders.
3. **Review.** Claims are checked against the catalog, the PDF is checked for
   page count, missing text and font substitution, the agent looks at the
   rendered pages, and a second reviewer reads the result before you do.
4. **It learns.** Your corrections become standing rules, and new experience
   goes into the catalog for next time.

Your data lives in a private workspace folder you choose. None of it belongs
in this repo.

## Install

Clone this repo into your agent's skills folder, for example:

```sh
git clone https://github.com/lakeczar/job-doc-builder ~/.claude/skills/job-doc-builder
pip install -r ~/.claude/skills/job-doc-builder/requirements.txt
```

PDF output needs [LibreOffice](https://www.libreoffice.org/), or Microsoft Word
on Windows. Without either, set the output format to Word only.

Then ask your agent: "Set up Job Doc Builder for me."

## Try it without an agent

```sh
python scripts/render.py --content examples/sample/resume.content.json \
    --template templates/classic/resume.docx --style templates/classic/resume.style.json \
    --out out/sample-resume
python scripts/check.py --content examples/sample/resume.content.json \
    --catalog examples/sample/catalog.json \
    --template templates/classic/resume.docx --style templates/classic/resume.style.json \
    --docx out/sample-resume.docx --pdf out/sample-resume.pdf --images out/pages
```

## Limits

- Templates must be single-column Word files built from ordinary paragraphs.
  Text inside tables, text boxes and multi-column sections is not filled.
- The checks are mechanical: they catch a missing source, an unsupported
  number, a clipped line or a swapped font. They cannot judge wording or
  honesty of emphasis. The agent's review and yours still matter.
- LibreOffice substitutes fonts it does not have (for example Calibri), which
  changes the look of the PDF. The check reports it.
- Tested so far with the starter templates on Windows with Word as the PDF
  converter. Other templates and LibreOffice conversion need wider testing.

## Layout

```text
SKILL.md        what the agent reads first
references/     wizard, application flow, review gates, file formats
scripts/        workspace setup, template inspection, rendering, checks
templates/      starter resume and cover letter
examples/       a fictional person's catalog and documents
```

## Credit

The idea of driving a job application workflow from an agent follows
[ai-job-search](https://github.com/MadsLorentzen/ai-job-search) by Mads
Lorentzen (MIT). No code from that project is included here.

## License

MIT. See [LICENSE](LICENSE).
