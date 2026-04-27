#!/usr/bin/env python3
"""init_session.py — 创建一个全新的 auto-dao 学习会话目录。

一次性生成 SKILL.md Step 3 所需的所有派生视图骨架：
    learning-history/{topic_id}_{timestamp}/
    ├── lessons/                (empty)
    ├── session_state.json      (schema v2.3, 必填字段已填)
    ├── summary.md              (模板原文)
    ├── roadmap_status.md       (模板原文)
    ├── _ai_context.md          (模板原文)
    ├── course_overview.md      (模板原文)
    ├── metrics.json            (模板原文 + session_id)
    └── review_queue.json       (模板原文)

AI 在 Step 3 调用此脚本后，只需就地填充模板里的 ``{placeholder}`` 业务内容。

用法：
    python scripts/session/init_session.py <topic_id> <source_path> [options]

示例：
    python scripts/session/init_session.py stm32-hal "tmp/stm32_manual.pdf" \
        --topic-name "STM32 HAL 入门" --learning-language zh --total-lessons 6

退出码：
    0  — 会话创建成功
    1  — 参数错误
    2  — 文件系统错误（目录已存在、模板缺失等）
"""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional


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

# --- Paths -----------------------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parents[2]
TEMPLATES_DIR = (
    PROJECT_ROOT
    / ".claude"
    / "skills"
    / "learning-engine"
    / "templates"
)
DEFAULT_HISTORY_BASE = PROJECT_ROOT / "learning-history"

# Mapping of logical name → (template filename, output filename)
# MD templates keep placeholders untouched so AI can fill them later.
_MD_COPY_SPEC = [
    ("summary-template.md", "summary.md"),
    ("roadmap-template.md", "roadmap_status.md"),
    ("ai-context-template.md", "_ai_context.md"),
    ("course-overview-template.md", "course_overview.md"),
]

_JSON_COPY_SPEC = [
    # metrics.json: copy template then set session_id
    ("metrics-template.json", "metrics.json"),
    # review_queue.json: copy as-is
    ("review-queue-template.json", "review_queue.json"),
]


# --- Helpers ---------------------------------------------------------------


def _iso_now() -> str:
    """ISO 8601 with UTC offset, second precision."""
    return (
        datetime.now(timezone.utc)
        .astimezone()
        .replace(microsecond=0)
        .isoformat()
    )


def _compute_source_hash(source_path: Path) -> str:
    """Return ``"sha256:<hex>"`` for an existing file, else ``""``."""
    if not source_path.exists() or not source_path.is_file():
        return ""
    h = hashlib.sha256()
    with source_path.open("rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return "sha256:" + h.hexdigest()


def _default_timestamp() -> str:
    """Filename-safe timestamp ``YYYY-MM-DD-HH-MM`` (local time)."""
    return datetime.now().strftime("%Y-%m-%d-%H-%M")


def _load_template_json(name: str) -> dict:
    path = TEMPLATES_DIR / name
    if not path.exists():
        raise FileNotFoundError(f"Missing template: {path}")
    return json.loads(path.read_text(encoding="utf-8"))


# --- Core ------------------------------------------------------------------


def init_session(
    topic_id: str,
    source_path: str,
    *,
    topic_name: Optional[str] = None,
    base_dir: Optional[Path] = None,
    timestamp: Optional[str] = None,
    learning_language: str = "",
    total_lessons: int = 0,
    processed_path: Optional[str] = None,
    repo_commit_hash: Optional[str] = None,
    force: bool = False,
) -> Path:
    """Create a new learning session directory and return its path.

    Args:
        topic_id: Human-readable slug (e.g. ``"stm32-hal"``), used in the
            folder name. ASCII + hyphens recommended.
        source_path: Path to the original learning material (can be a file,
            directory, or URL string — validated only loosely).
        topic_name: Display name; defaults to ``topic_id`` if omitted.
        base_dir: Parent dir for sessions; defaults to
            ``<project>/learning-history``.
        timestamp: Force a timestamp suffix (for deterministic tests);
            defaults to local ``YYYY-MM-DD-HH-MM``.
        learning_language: ISO 639-1 code or empty string.
        total_lessons: Roadmap-level planned total; 0 when unknown.
        processed_path: Markdown-converted path; defaults to ``source_path``
            for already-Markdown inputs.
        repo_commit_hash: Git HEAD hash for repo-based materials.
        force: If True and the target directory already exists, overwrite it.

    Returns:
        Absolute Path of the created session directory.

    Raises:
        FileExistsError: When target exists and ``force`` is False.
        FileNotFoundError: When a required template is missing.
    """
    if not topic_id:
        raise ValueError("topic_id must be non-empty")
    if not source_path:
        raise ValueError("source_path must be non-empty")

    base = Path(base_dir) if base_dir else DEFAULT_HISTORY_BASE
    ts = timestamp or _default_timestamp()
    session_dir = base / f"{topic_id}_{ts}"

    if session_dir.exists():
        if force:
            shutil.rmtree(session_dir)
        else:
            raise FileExistsError(
                f"Session directory already exists: {session_dir}"
            )

    # Create directory tree
    lessons_dir = session_dir / "lessons"
    lessons_dir.mkdir(parents=True, exist_ok=True)
    for child in ("learn", "practice", "deep"):
        (lessons_dir / child).mkdir(parents=True, exist_ok=True)
    (session_dir / "source_coverage").mkdir(parents=True, exist_ok=True)

    # Copy Markdown templates verbatim (placeholders preserved for AI to fill)
    for tpl_name, out_name in _MD_COPY_SPEC:
        tpl_path = TEMPLATES_DIR / tpl_name
        if not tpl_path.exists():
            raise FileNotFoundError(f"Missing template: {tpl_path}")
        shutil.copyfile(tpl_path, session_dir / out_name)

    # Initialise JSON artefacts
    for tpl_name, out_name in _JSON_COPY_SPEC:
        data = _load_template_json(tpl_name)
        if out_name == "metrics.json":
            data["session_id"] = str(uuid.uuid4())
        (session_dir / out_name).write_text(
            json.dumps(data, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

    # Build session_state.json from template + overrides
    state = _load_template_json("session-state-template.json")
    now = _iso_now()
    state.update(
        {
            "topic_id": topic_id,
            "topic_name": topic_name or topic_id,
            "source_path": source_path,
            "processed_path": processed_path or source_path,
            "source_hash": _compute_source_hash(Path(source_path)),
            "phase": "learning",
            "total_lessons": total_lessons,
            "learning_language": learning_language,
            "repo_commit_hash": repo_commit_hash,
            "created_at": now,
            "updated_at": now,
        }
    )
    # Seed learner_model.last_updated_at too for schema compliance
    state["learner_model"]["last_updated_at"] = now
    (session_dir / "session_state.json").write_text(
        json.dumps(state, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    return session_dir


# --- CLI -------------------------------------------------------------------


def _parse_args(argv: list[str]) -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description="Create a fresh auto-dao learning session directory.",
    )
    p.add_argument("topic_id", help="Slug-style topic id (ASCII, e.g. 'stm32-hal')")
    p.add_argument("source_path", help="Path to the original learning material")
    p.add_argument("--topic-name", default=None, help="Display name; defaults to topic_id")
    p.add_argument("--base", default=None, help="Parent directory (default: learning-history/)")
    p.add_argument("--timestamp", default=None, help="Timestamp suffix YYYY-MM-DD-HH-MM")
    p.add_argument("--learning-language", default="", help="ISO 639-1 code (e.g. 'zh')")
    p.add_argument("--total-lessons", type=int, default=0, help="Planned total lessons")
    p.add_argument("--processed-path", default=None, help="Markdown-converted path")
    p.add_argument("--repo-commit-hash", default=None, help="Git HEAD hash for repo materials")
    p.add_argument("--force", action="store_true", help="Overwrite existing directory")
    return p.parse_args(argv)


def main(argv: Optional[list[str]] = None) -> int:
    args = _parse_args(argv if argv is not None else sys.argv[1:])
    try:
        session_dir = init_session(
            topic_id=args.topic_id,
            source_path=args.source_path,
            topic_name=args.topic_name,
            base_dir=Path(args.base) if args.base else None,
            timestamp=args.timestamp,
            learning_language=args.learning_language,
            total_lessons=args.total_lessons,
            processed_path=args.processed_path,
            repo_commit_hash=args.repo_commit_hash,
            force=args.force,
        )
    except ValueError as e:
        print(f"❌ Invalid argument: {e}", file=sys.stderr)
        return 1
    except FileExistsError as e:
        print(f"❌ {e}\n    Use --force to overwrite.", file=sys.stderr)
        return 2
    except FileNotFoundError as e:
        print(f"❌ {e}", file=sys.stderr)
        return 2

    print(f"✅ Session created: {session_dir}")
    print("Next steps:")
    print("  1. Fill in placeholders inside summary.md / roadmap_status.md / course_overview.md")
    print(f"  2. Validate: python scripts/session/validate_state.py {session_dir}")
    print("  3. Proceed with SKILL.md Step 3.5 (pre-assessment) or Step 4 (lesson generation)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
