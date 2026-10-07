# Setup wizard

Run once per person. Each step ends by adding its name to `completed` in
`wizard-state.json` and setting `next`, so the person can stop and resume.
Tell them up front: there are six steps, the catalog interview is the long one
(20 to 40 minutes), and it is the step that makes every later document better.

Steps: `base-documents`, `profile`, `catalog`, `rules-and-voice`, `style`, `first-render`.

## 1. base-documents

Ask which describes them:

- **"I have a resume (and maybe a cover letter)."** Ask for the files. Copy them
  to `imports/` untouched. Read them with `extract_text.py`. Ask whether they
  are current; if not, note what is missing or out of date for step 3.
- **"I'm starting from scratch."** Fine. Steps 2 and 3 produce the material and
  step 6 writes the first resume. Use the starter templates
  (`init_workspace.py <workspace> --starter`).

Also ask whether they like how their current resume looks. That decides step 5.

## 2. profile

Fill `profile.json`: name as they want it printed, email, phone, city, links
(LinkedIn, portfolio, GitHub), target roles and seniority, work authorization
if relevant, anything about location or remote preference. Read back what you
took from their resume and let them correct it rather than asking from zero.

## 3. catalog

This is the moment that matters. Build `catalog.json` by interview, one entry
at a time: each job, then projects, education, certifications, volunteer and
anything else. Seed entries from the imported resume, then go deeper than the
resume does.

For each role, ask until you have facts, not adjectives:

- What did you own? What was the team and your part in it?
- What changed because of your work? Is there a number, and how do you know it?
- What was hard about it? What would have gone wrong without you?
- What tools and methods did you actually use, hands on?
- Who did you work with or lead?

Write each answer as a fact with a confidence:

- `confirmed`: they are sure and could defend it in an interview.
- `approximate`: the size is right but the figure is a recollection. Wording
  must say "about" or "roughly".
- `unverified`: they are not sure. Do not use it in a document until resolved.

Then ask the questions resumes leave out:

- Work you are proud of that never made it onto a resume.
- Side projects, freelance, open source, teaching, speaking, writing.
- Things you did outside your job title.
- Gaps in the timeline: what were you doing? They decide how it is shown.
- Tools you have used but would not call a strength.

Build the skills list last, from the facts. Each skill gets a level in their own
words and the fact ids that back it. A skill with no evidence is marked as
such; it can appear in a skills line but must not be dressed up in a bullet.

Read the catalog back in plain language, section by section, and correct it
with them. Nothing goes in that they have not confirmed.

## 4. rules-and-voice

Fill `rules.md`:

- **Never claim**: titles they did not hold, tools they have only read about,
  employers or clients they cannot name, anything under NDA.
- **Always keep**: sections, employers or wording that must not be cut or
  reworded (for example an exact job title or a certification name).
- **Tailoring preferences**: how far tailoring may go. May the summary be
  rewritten per job? May bullets be reordered or dropped? May older roles be
  shortened?

For the cover letter voice, ask for one or two things they wrote themselves
(an old letter, an email, a post) and save them in `voice/`. Note how they
write: sentence length, formality, how they open and close. If they have none,
ask three questions about tone and write a short sample for them to edit.

## 5. style

Goal: a template `.docx`, a style map and a contract for each document.

**They like their current resume's look.** Copy the `.docx` to
`base/resume.docx` and run:

```sh
python scripts/inspect_template.py base/resume.docx
```

Give each kind of paragraph a role and write `base/resume.style.json` pointing
each role at one paragraph that shows its formatting. Typical roles: `name`,
`contact`, `section`, `body`, `entry`, `bullet`, `skills`. Add roles if their
resume has more kinds of line (for example a separate `entry_dates` line).

If the tool warns about tables, text boxes or columns, tell the person: those
layouts cannot be filled reliably and often read badly in applicant tracking
systems. Offer the starter template, or ask them to supply a single-column
version. If they only have a PDF, there is no Word template to keep; use the
starter template and match their fonts and section order as closely as it
allows.

**They are starting fresh or want a new look.** Use the starter templates. If
they want changes (font, margins, heading style), they or you edit the starter
`.docx` in Word and re-run `inspect_template.py`.

Set the contract in each style map: `page_limit`, and the section order if it
is fixed. Ask; do not assume one page.

Do the same for the cover letter.

## 6. first-render

Write `base/resume.content.json` from the catalog (and their existing resume
wording where it is accurate), then render and review it using
[review.md](review.md). If they brought a resume, compare your render with
their original side by side; it should look the same. Fix the style map until
it does.

Show them the result. When they approve it, the base is set. Write the base
cover letter content the same way if they want one.

Finish by telling them what they can now do: paste a job link, paste
application questions, or tell you about new experience at any time.
