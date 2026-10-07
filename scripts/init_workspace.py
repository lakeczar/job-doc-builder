#!/usr/bin/env python3
"""Create a private career workspace. Safe to run again: existing files are kept.

  python init_workspace.py ~/career            # empty workspace
  python init_workspace.py ~/career --starter  # also copy the starter templates into base/

The workspace holds personal data. Keep it out of any shared or public repo.
"""
import argparse
import json
import shutil
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent

FILES = {
    "settings.json": {"formats": ["docx", "pdf"], "resume_page_limit": 2, "cover_letter_page_limit": 1},
    "profile.json": {"name": "", "email": "", "phone": "", "location": "", "links": [], "target_roles": [], "work_authorization": ""},
    "catalog.json": {"entries": [], "skills": []},
    "wizard-state.json": {"completed": [], "next": "base-documents"},
}
RULES = """# Rules

The agent reads this before every draft and adds to it when you correct something.

## Never claim

## Always keep

## Tailoring preferences

## Learned from your edits
"""


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("workspace")
    ap.add_argument("--starter", action="store_true", help="copy the starter resume and cover letter templates into base/")
    args = ap.parse_args()

    root = Path(args.workspace).expanduser()
    for folder in ("base", "voice", "applications", "imports"):
        (root / folder).mkdir(parents=True, exist_ok=True)
    for name, data in FILES.items():
        if not (root / name).exists():
            (root / name).write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
    if not (root / "rules.md").exists():
        (root / "rules.md").write_text(RULES, encoding="utf-8")
    if not (root / ".gitignore").exists():
        # If someone does put this folder under git, nothing personal is tracked by accident.
        (root / ".gitignore").write_text("*\n", encoding="utf-8")
    if args.starter:
        for source in sorted((REPO / "templates" / "classic").iterdir()):
            target = root / "base" / source.name
            if not target.exists():
                shutil.copy2(source, target)
    print(f"workspace ready at {root}")


if __name__ == "__main__":
    main()
