#!/usr/bin/env python3
"""
check_examples.py — Validate example learning-history directory structure.

Each example session under examples/learning-history/ must contain:
  - summary.md
  - roadmap_status.md
  - lessons/           (directory with at least one legacy lesson_N.md or
                        one current structured Markdown lesson)

Exit codes:
    0  — all examples valid
    1  — one or more examples invalid
"""

import re
import sys
from pathlib import Path

# Ensure UTF-8 stdout even on Windows PowerShell (default cp936/GBK can't emit ✅ / ❌).
if sys.stdout.encoding and sys.stdout.encoding.lower() not in ("utf-8", "utf8"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")  # type: ignore[union-attr]
        sys.stderr.reconfigure(encoding="utf-8")  # type: ignore[union-attr]
    except Exception:
        pass  # Python <3.7 fallback; CI runs on 3.11+ so this is cosmetic.

EXAMPLES_ROOT = Path("examples/learning-history")

REQUIRED_FILES = ["summary.md", "roadmap_status.md"]
SKIP = {"README.md"}


def check_session(session_dir: Path) -> list[str]:
    """Return list of error messages for a single session directory."""
    errors = []

    for fname in REQUIRED_FILES:
        if not (session_dir / fname).exists():
            errors.append(f"missing {fname}")

    lessons_dir = session_dir / "lessons"
    if not lessons_dir.is_dir():
        errors.append("missing lessons/ directory")
    else:
        lesson_files = [
            f for f in lessons_dir.iterdir()
            if f.is_file() and re.match(r"lesson_\d+\.md$", f.name)
        ]
        if not lesson_files:
            lesson_files = [
                f for f in lessons_dir.rglob("*.md")
                if f.is_file() and not f.name.startswith("_")
            ]
        if not lesson_files:
            errors.append("lessons/ contains no lesson markdown files")

    return errors


def main():
    if not EXAMPLES_ROOT.is_dir():
        print(f"ERROR: {EXAMPLES_ROOT} not found")
        sys.exit(1)

    sessions = [
        d for d in EXAMPLES_ROOT.iterdir()
        if d.is_dir() and d.name not in SKIP
    ]

    if not sessions:
        print(f"WARNING: no example sessions found in {EXAMPLES_ROOT}")
        sys.exit(0)

    total_errors = 0

    for session in sorted(sessions):
        errors = check_session(session)
        if errors:
            total_errors += len(errors)
            for err in errors:
                print(f"❌ {session.name}: {err}")
        else:
            print(f"✅ {session.name}")

    print(f"\n{'=' * 40}")
    print(f"Checked {len(sessions)} examples, {total_errors} errors")

    sys.exit(0 if total_errors == 0 else 1)


if __name__ == "__main__":
    main()
