# Application flow

Input: a job link, a pasted description, application questions, or any mix,
plus optional instructions ("emphasise the platform work", "letter only").

Work in a new folder: `applications/<YYYY-MM-DD>-<company>-<role>/`. Never
write into `base/` here.

## 1. Capture the job

Save the posting text as `job.md` with the source link and the date you read
it. If you cannot fetch a link, ask them to paste the text. If the posting is
closed, behind a login, or redirects to a different job, stop and say so.

## 2. Map requirements to evidence

Write `requirement-map.json`: each real requirement or preference in the
posting, and where the person stands.

- `supported`: catalog facts back it directly. List the ids.
- `adjacent`: related experience, honestly not the same thing. List the ids
  and say what the difference is.
- `gap`: nothing in the catalog.

Show the person a short version: strongest matches, adjacent ones, gaps.

## 3. Ask about the gaps

For each gap or thin area, ask once: "The posting asks for X. Have you done
anything like that?" New facts go into `catalog.json` with a confidence and a
source of "interview <date>" before you use them. This is how the catalog
grows. If the answer is no, it stays a gap and stays out of the documents.

If the job is a poor fit on the hard requirements, say so before drafting and
let them decide whether to continue.

## 4. Draft

Start from the base content and change only what tailoring allows under
`rules.md`.

**Resume** (`resume.content.json`):
- Reorder and choose bullets so the first third of the page answers the
  posting's main requirements.
- Use the posting's terms where they are true of the person ("CI/CD" rather
  than "build pipelines" if they did CI/CD). Do not add a keyword that no fact
  supports.
- Every block that makes a claim carries `evidence` ids.
- Stay inside the page limit by cutting the least relevant content, never by
  shrinking fonts or margins.

**Cover letter** (`cover-letter.content.json`):
- Three or four short paragraphs: why this role, two pieces of evidence that
  match what they need, a plain close.
- Written in the person's voice from `voice/`. No stock phrases, no restating
  the resume.
- Name the company and role correctly. Check both against `job.md`.

**Application questions** (`answers.content.json`):
- One `question` block followed by `body` blocks for each answer, with
  evidence. Respect any stated length limit and say the length you hit.
- For questions about salary, relocation, work authorization, notice period or
  demographics, do not guess: ask the person, or use `profile.json` if they
  have recorded an answer there.

Produce only what was asked for. Default is resume and cover letter.

## 5. Review, render, review again

Follow [review.md](review.md). In short: claims check on the content, render,
mechanical check on the output, look at the pages, a fresh second review, then
show the person.

## 6. Present

Give them:
- The files, in the formats from `settings.json` (Word and PDF unless they
  changed it).
- What changed against their base, in a few lines.
- What the posting asked for that is not covered, and why.
- Anything you were unsure about.

## 7. Learn from their edits

When they change something, apply it, and ask whether it is a one-off or a
standing preference. Standing preferences go into `rules.md` under "Learned
from your edits", in their words, with the date. If an edit corrects a fact,
fix `catalog.json`, not just the document.

Changes to the base documents happen only when they say to promote something
("use this summary from now on"). Copy the approved content into `base/` then.

Record the outcome if they tell you (applied, interview, rejected) in
`application.json` in the same folder. This skill does not submit applications
or track them on its own.
