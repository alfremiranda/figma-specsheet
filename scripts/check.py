#!/usr/bin/env python3
"""Structural checks for the skill. Run locally or in CI: python3 scripts/check.py"""
from __future__ import annotations

import re
import re as _rx
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SKILL = ROOT / "SKILL.md"
OLD_NAME = "document-figma-component"

errors: list[str] = []
notes: list[str] = []


def md_files() -> list[Path]:
    return sorted(p for p in ROOT.rglob("*.md") if ".git" not in p.parts and "dist" not in p.parts)


# 1. frontmatter
text = SKILL.read_text(encoding="utf-8")
if not text.startswith("---\n"):
    errors.append("SKILL.md must open with a --- frontmatter fence")
else:
    fm = text.split("---\n", 2)[1]
    if not re.search(r"^name: [a-z0-9-]+$", fm, re.M):
        errors.append("SKILL.md frontmatter: missing or malformed `name:` (lowercase kebab-case)")
    if not re.search(r"^description: \S.{40,}", fm, re.M):
        errors.append("SKILL.md frontmatter: `description:` missing or too short to route on")
    else:
        notes.append("frontmatter ok")

# 2. the old name may survive in the changelog (it records the rename) but nowhere else
for p in md_files():
    if p.name == "CHANGELOG.md":
        continue
    for i, line in enumerate(p.read_text(encoding="utf-8").splitlines(), 1):
        if OLD_NAME in line:
            errors.append(f"{p.relative_to(ROOT)}:{i}: stale skill name `{OLD_NAME}`")

# 3. relative markdown links resolve
LINK = re.compile(r"\[[^\]]*\]\(([^)\s]+)\)")
checked = 0
for p in md_files():
    for i, line in enumerate(p.read_text(encoding="utf-8").splitlines(), 1):
        for target in LINK.findall(line):
            if target.startswith(("http://", "https://", "#", "mailto:")):
                continue
            # GitHub repo-relative shorthand (../../releases, ../../issues) resolves on
            # github.com but not on disk
            if re.match(r"\.\./\.\./(releases|issues|pulls|wiki|discussions)\b", target):
                continue
            path = target.split("#", 1)[0]
            if not path:
                continue
            checked += 1
            if not (p.parent / path).exists():
                errors.append(f"{p.relative_to(ROOT)}:{i}: broken link -> {target}")
notes.append(f"{checked} relative links checked")

# 4. every reference file is linked from SKILL.md, and every link points at a real file
refs = sorted((ROOT / "references").glob("*.md"))
if not refs:
    errors.append("references/ is empty")
for r in refs:
    if r.stat().st_size == 0:
        errors.append(f"{r.relative_to(ROOT)} is empty")
    if f"references/{r.name}" not in text:
        errors.append(f"{r.relative_to(ROOT)} is never linked from SKILL.md — it will never load")
notes.append(f"{len(refs)} reference files, all linked")

# 5. no real Figma file keys committed
KEY = re.compile(r"figma\.com/(?:design|file)/([A-Za-z0-9]{15,})")
for p in md_files():
    for i, line in enumerate(p.read_text(encoding="utf-8").splitlines(), 1):
        m = KEY.search(line)
        if m and "<" not in m.group(1):
            errors.append(f"{p.relative_to(ROOT)}:{i}: live Figma file key in a public repo")

# 6. no real person's handle in a worked example (rubric I0: owners are display names)
HANDLE = _rx.compile(r"(?<![\w`/])@[A-Za-z][A-Za-z0-9._-]{2,}")
ALLOWED_AT = ("@theme", "@media", "@import", "@layer", "@supports", "@keyframes", "@apply")
for p in md_files():
    if p.name == "CHANGELOG.md":
        continue
    for i, line in enumerate(p.read_text(encoding="utf-8").splitlines(), 1):
        for m in HANDLE.finditer(line):
            if m.group(0).lower().startswith(ALLOWED_AT):
                continue
            errors.append(
                f"{p.relative_to(ROOT)}:{i}: `{m.group(0)}` — a worked example must not carry "
                f"a real handle; owners render as display names (I0)"
            )
notes.append("no handles in worked examples")

# 7. the section-discovery contract must constrain type and parent everywhere it appears
BARE_DISCOVERY = _rx.compile(r"findAll\(\s*n\s*=>\s*/\^\\d\\d")
for p in md_files():
    lines = p.read_text(encoding="utf-8").splitlines()
    for i, line in enumerate(lines, 1):
        if not BARE_DISCOVERY.search(line) or "n.type" in line:
            continue
        # a deliberately-labelled counter-example is allowed
        window = " ".join(lines[max(0, i - 3):i])
        if "WRONG" in window or "// WRONG" in line:
            continue
        errors.append(
                f"{p.relative_to(ROOT)}:{i}: bare section-discovery regex — it also matches "
                f"auto-named TEXT nodes; constrain n.type === 'FRAME' and the parent"
            )
notes.append("discovery contract constrained")

# 8. changelog has a version heading package.sh can read
if not re.search(r"^## v\d+\.\d+(\.\d+)?", (ROOT / "CHANGELOG.md").read_text(encoding="utf-8"), re.M):
    errors.append("CHANGELOG.md: no `## vX.Y[.Z]` heading — scripts/package.sh cannot resolve a version")
else:
    notes.append("changelog version heading ok")

for n in notes:
    print(f"  ok  {n}")
for e in errors:
    print(f"FAIL  {e}", file=sys.stderr)
print(f"\n{len(errors)} problem(s)")
sys.exit(1 if errors else 0)
