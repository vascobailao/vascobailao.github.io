#!/usr/bin/env python3
"""
Daily course-day publisher.

Reads posts/course/course-spec.yaml, finds the next upcoming day, asks
Claude to generate a complete course-day HTML file that meets the
strict content contract (5+ super labs, executable code, deliverables,
no em dashes, vendor-neutral, technically deep), validates the output,
writes the file, updates the course index status, and commits.

Refuses to publish if validation fails.

Required env:
  ANTHROPIC_API_KEY   for generation
  GITHUB_TOKEN        for git push (workflow provides it)

Run:
  python scripts/publish_next_day.py            # publish next day
  python scripts/publish_next_day.py --dry-run  # generate only
  python scripts/publish_next_day.py --day 2    # force a specific day
"""
from __future__ import annotations

import argparse
import os
import re
import subprocess
import sys
from pathlib import Path

import yaml
from anthropic import Anthropic

ROOT = Path(__file__).resolve().parent.parent
SPEC_PATH = ROOT / "posts" / "course" / "course-spec.yaml"
COURSE_DIR = ROOT / "posts" / "course"
INDEX_PATH = COURSE_DIR / "index.html"

MODEL = "claude-opus-4-7"
MAX_TOKENS = 16000

# Hard validation bars. Generation that fails any of these is rejected.
REQUIRED_LAB_COUNT = 5
FORBIDDEN_CHARS = ["—"]  # em dash
FORBIDDEN_PHRASES = [
    "in today's fast-paced",
    "leverage", "robust", "seamless", "cutting-edge",
    "revolutionary", "game-changer", "synergy",
    "unlock the power", "harness the power",
]
REQUIRED_TOKENS = [
    'class="lab"',
    'class="lab-deliv"',
    'class="nb-cell"',
    "Deliverable",
]


def load_spec() -> dict:
    return yaml.safe_load(SPEC_PATH.read_text())


def find_next_day(spec: dict, force_day: int | None = None) -> dict:
    days = spec["days"]
    if force_day is not None:
        for d in days:
            if d["day"] == force_day:
                return d
        raise SystemExit(f"day {force_day} not in spec")
    upcoming = [d for d in days if d["status"] == "upcoming"]
    if not upcoming:
        raise SystemExit("no upcoming days; course is complete")
    return upcoming[0]


def reference_html() -> str:
    """Day 1 is the canonical example; we hand it to the model verbatim."""
    return (COURSE_DIR / "day-01-the-landscape.html").read_text()


def build_prompt(spec: dict, day: dict) -> str:
    course = spec["course"]
    reqs = course["required_per_day"]
    must_inc = "\n".join(f"  - {x}" for x in reqs["must_include"])
    must_avoid = "\n".join(f"  - {x}" for x in reqs["must_avoid"])
    depth = "\n".join(f"  - {x}" for x in day.get("technical_depth_requirements", []))
    labs = "\n".join(f"  {i+1}. {x}" for i, x in enumerate(day.get("labs", [])))
    return f"""You are publishing Day {day['day']} of "{course['title']}".

# Voice and style
{course['voice']}.
The audience is {course['audience']}. Write the way an experienced engineer
talks to other experienced engineers: direct, evidence-driven, opinionated
where opinions are earned, honest about limits.

# Content contract (HARD requirements; validation will reject violations)
- Exactly one HTML file, complete, standalone, matching the visual style
  of the reference Day 1 file provided below.
- Minimum {reqs['min_labs']} labs. Each lab must have:
    * Numbered tag (Lab 01, Lab 02, ...)
    * Estimated time
    * Difficulty
    * Step-by-step instructions
    * At least one executable code block (use the .nb-cell pattern)
    * An explicit "Deliverable" closing the lab (use the .lab-deliv pattern)
    * Acceptance criteria: the reader knows when the lab is done
- Total reading time {reqs['min_read_minutes']}+ minutes including labs.
- Lab content totalling {reqs['min_lab_minutes']}+ minutes.
- Must include:
{must_inc}
- Must avoid:
{must_avoid}

NEVER use em dashes (U+2014). Use commas, colons, periods, parentheses,
or restructure the sentence. This is non-negotiable.
NEVER use marketing-flavoured words (leverage, robust, seamless,
cutting-edge, revolutionary, game-changer, synergy, harness the power).

# This day's brief
Day {day['day']}: {day['title']}
Date: {day['date']}
Theme: {day['theme']}

Required technical depth:
{depth}

Required labs (treat as the minimum; you may go deeper):
{labs}

# Structural template (use the same CSS classes and DOM shape as the reference)
- <head> with the same fonts and inline CSS
- <nav> linking back to course index
- .post-header with crumb, label "Day {day['day']} of 14 / Hands-on / 5+ labs",
  title, post-meta (date, time, lab count), tags
- .post-body with intro paragraphs, h2 sections, theory then labs interleaved
  or clustered, then a "What You Should Take Away" section, then a
  "Tomorrow" teaser pointing at Day {day['day']+1 if day['day'] < 14 else 'wrap-up'}.
- .post-footer linking back to course index and contact
- <footer> matching reference

# Reference (Day 1, for visual + structural matching)
The HTML below is the canonical example. Match its tag structure, CSS class
usage, and prose density. DO NOT copy its content.

```html
{reference_html()}
```

# Output
Return ONLY the complete HTML for Day {day['day']}, starting with
<!DOCTYPE html> and ending with </html>. No commentary before or after.
"""


def generate(prompt: str) -> str:
    client = Anthropic()
    msg = client.messages.create(
        model=MODEL,
        max_tokens=MAX_TOKENS,
        messages=[{"role": "user", "content": prompt}],
    )
    out = "".join(b.text for b in msg.content if b.type == "text")
    # Some models occasionally wrap in fences despite instructions
    out = re.sub(r"^```(?:html)?\s*", "", out)
    out = re.sub(r"\s*```$", "", out)
    return out.strip()


class ValidationError(Exception):
    pass


def validate(html: str, day: dict) -> None:
    problems: list[str] = []

    if not html.lstrip().startswith("<!DOCTYPE html>"):
        problems.append("missing doctype")
    if "</html>" not in html:
        problems.append("missing closing html tag")

    for ch in FORBIDDEN_CHARS:
        if ch in html:
            count = html.count(ch)
            problems.append(f"forbidden char U+{ord(ch):04X} appears {count} times")

    lower = html.lower()
    for phrase in FORBIDDEN_PHRASES:
        if phrase in lower:
            problems.append(f"forbidden marketing phrase: {phrase!r}")

    for token in REQUIRED_TOKENS:
        if token not in html:
            problems.append(f"missing required token: {token!r}")

    lab_count = len(re.findall(r'class="lab-tag">Lab \d+', html))
    if lab_count < REQUIRED_LAB_COUNT:
        problems.append(f"only {lab_count} labs (need {REQUIRED_LAB_COUNT}+)")

    deliv_count = len(re.findall(r'class="lab-deliv-label">Deliverable', html))
    if deliv_count < REQUIRED_LAB_COUNT:
        problems.append(f"only {deliv_count} deliverables (need {REQUIRED_LAB_COUNT}+)")

    title = day["title"]
    if title not in html:
        problems.append(f"day title not present in body: {title!r}")

    # Heuristic: a "super lab" should have at least one nb-cell of code
    nb_cells = len(re.findall(r'class="nb-cell"', html))
    if nb_cells < REQUIRED_LAB_COUNT:
        problems.append(
            f"only {nb_cells} code cells (need {REQUIRED_LAB_COUNT}+ for super labs)"
        )

    if problems:
        raise ValidationError("\n  - " + "\n  - ".join(problems))


def file_for(day: dict) -> Path:
    return COURSE_DIR / f"day-{day['day']:02d}-{day['slug']}.html"


def update_spec_status(day_num: int) -> None:
    """Mark a day as published in the spec."""
    text = SPEC_PATH.read_text()
    pattern = re.compile(
        rf"(  - day: {day_num}\n"
        rf"    slug: \"[^\"]+\"\n"
        rf"    date: \"[^\"]+\"\n"
        rf"    status: )upcoming",
    )
    new = pattern.sub(r"\1published", text, count=1)
    if new == text:
        raise SystemExit(f"could not flip status for day {day_num} in spec")
    SPEC_PATH.write_text(new)


def update_index(day: dict) -> None:
    """Flip the day's card in the index from upcoming to published."""
    text = INDEX_PATH.read_text()
    day_num_str = f"DAY<strong>{day['day']:02d}</strong>"
    href = file_for(day).name
    # find the upcoming card for this day and rewrite it
    pattern = re.compile(
        r'<div class="day-card upcoming">\s*'
        r'<div class="day-num">DAY<strong>'
        + f"{day['day']:02d}"
        + r'</strong></div>\s*'
        r'<div class="day-content">\s*'
        r'<div class="day-title">[^<]+</div>\s*'
        r'<div class="day-desc">([^<]+)</div>\s*'
        r'</div>\s*'
        r'<div class="day-meta"><span class="day-status">UPCOMING</span><br>([^<]+)</div>\s*'
        r'</div>',
        re.DOTALL,
    )
    m = pattern.search(text)
    if not m:
        raise SystemExit(f"could not find upcoming card for day {day['day']}")
    desc = m.group(1).strip()
    meta = m.group(2).strip()
    replacement = (
        f'<a class="day-card published" href="{href}">\n'
        f'          <div class="day-num">DAY<strong>{day["day"]:02d}</strong></div>\n'
        f'          <div class="day-content">\n'
        f'            <div class="day-title">{day["title"]}</div>\n'
        f'            <div class="day-desc">{desc}</div>\n'
        f'          </div>\n'
        f'          <div class="day-meta"><span class="day-status done">PUBLISHED</span><br>{meta} · 5 labs</div>\n'
        f'        </a>'
    )
    INDEX_PATH.write_text(text[: m.start()] + replacement + text[m.end():])


def git_commit_and_push(day: dict, dry_run: bool) -> None:
    if dry_run:
        print("[dry-run] skipping git operations")
        return
    subprocess.check_call(["git", "config", "user.name", "course-bot"])
    subprocess.check_call(["git", "config", "user.email", "course-bot@users.noreply.github.com"])
    subprocess.check_call([
        "git", "add",
        str(file_for(day)),
        str(INDEX_PATH),
        str(SPEC_PATH),
    ])
    msg = f"Publish Day {day['day']:02d}: {day['title']}"
    subprocess.check_call(["git", "commit", "-m", msg])
    subprocess.check_call(["git", "push", "origin", "HEAD:master"])


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--dry-run", action="store_true")
    p.add_argument("--day", type=int, default=None)
    args = p.parse_args()

    if "ANTHROPIC_API_KEY" not in os.environ:
        print("ANTHROPIC_API_KEY not set", file=sys.stderr)
        return 2

    spec = load_spec()
    day = find_next_day(spec, args.day)
    out_path = file_for(day)
    if out_path.exists() and not args.dry_run:
        print(f"already published: {out_path}", file=sys.stderr)
        return 0

    print(f"generating Day {day['day']}: {day['title']}")
    prompt = build_prompt(spec, day)
    html = generate(prompt)

    try:
        validate(html, day)
    except ValidationError as e:
        # one retry with a critique-and-revise loop
        print(f"validation failed:{e}\nattempting one revision pass")
        critique = (
            f"Your previous output failed validation with the following issues:"
            f"{e}\n\n"
            f"Regenerate the complete HTML file fixing every issue. "
            f"Do not change anything that already passed."
        )
        html = generate(prompt + "\n\n# REVISION REQUEST\n" + critique)
        validate(html, day)

    out_path.write_text(html)
    update_spec_status(day["day"])
    update_index(day)
    print(f"wrote {out_path}")

    git_commit_and_push(day, args.dry_run)
    print(f"published Day {day['day']:02d}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
