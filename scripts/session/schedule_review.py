#!/usr/bin/env python3
"""
schedule_review.py — Calculate and display pending review items.

Reads review_queue.json from a learning session directory,
checks which items are due for review, and prints a summary.

Usage:
    python scripts/session/schedule_review.py <session_dir>

Exit codes:
    0  — no reviews due (or no queue file)
    2  — reviews are due (informational, not an error)
"""

import json
import sys
from datetime import datetime, timezone
from pathlib import Path


def _ensure_utf8_stdio() -> None:
    """Avoid UnicodeEncodeError for emoji/status output on Windows consoles."""
    for stream in (sys.stdout, sys.stderr):
        encoding = getattr(stream, "encoding", "") or ""
        if encoding.lower() in ("utf-8", "utf8"):
            continue
        try:
            stream.reconfigure(encoding="utf-8")  # type: ignore[attr-defined]
        except Exception:
            pass


_ensure_utf8_stdio()


def load_queue(session_dir: Path) -> dict:
    queue_path = session_dir / "review_queue.json"
    if not queue_path.exists():
        return {"schema_version": "1.0", "items": []}
    with open(queue_path, "r", encoding="utf-8") as f:
        return json.load(f)


def get_due_items(queue: dict, now: datetime | None = None) -> list[dict]:
    """Return items whose next_review_at is in the past and status is pending."""
    if now is None:
        now = datetime.now(timezone.utc)
    due = []
    for item in queue.get("items", []):
        if item.get("status") != "pending":
            continue
        next_review = item.get("next_review_at")
        if next_review:
            review_dt = datetime.fromisoformat(next_review)
            # Ensure UTC-aware comparison: if naive, assume local; if aware, normalize to UTC
            if review_dt.tzinfo is None:
                review_dt = review_dt.replace(tzinfo=timezone.utc)
            else:
                review_dt = review_dt.astimezone(timezone.utc)
            if review_dt <= now:
                due.append(item)
    return due


def main():
    if len(sys.argv) != 2:
        print("Usage: schedule_review.py <session_dir>")
        sys.exit(1)

    session_dir = Path(sys.argv[1])
    if not session_dir.is_dir():
        print(f"Error: '{session_dir}' is not a directory")
        sys.exit(1)

    queue = load_queue(session_dir)
    due = get_due_items(queue)

    if not due:
        print("✅ No reviews due.")
        sys.exit(0)

    print(f"📋 {len(due)} review(s) due:\n")
    for item in due:
        print(f"  - Lesson {item['lesson']}, Q{item['question_index']}: "
              f"{item.get('topic_tag', 'N/A')} "
              f"(wrong: {item.get('first_wrong_at', '?')}, "
              f"reviews: {item.get('review_count', 0)})")

    sys.exit(2)


if __name__ == "__main__":
    main()
