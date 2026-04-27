#!/usr/bin/env python3
"""Reconcile session_state.json against the lesson files on disk.

Default mode is read-only. Use explicit --fix-* flags to write changes; every
write creates a timestamped backup next to session_state.json first.
"""

from __future__ import annotations

import argparse
import json
import re
import shutil
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Sequence


def _ensure_utf8_stdio() -> None:
    """Avoid UnicodeEncodeError for Chinese lesson filenames on Windows consoles."""
    for stream in (sys.stdout, sys.stderr):
        encoding = getattr(stream, "encoding", "") or ""
        if encoding.lower() in ("utf-8", "utf8"):
            continue
        try:
            stream.reconfigure(encoding="utf-8")  # type: ignore[attr-defined]
        except Exception:
            pass


_ensure_utf8_stdio()

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from scripts.session.validate_state import (  # noqa: E402
    VALID_WAIT_REASONS,
    _active_lesson_files,
    _lesson_id_from_filename,
    _lesson_path,
)


@dataclass(frozen=True)
class ReconcileFinding:
    kind: str
    message: str
    suggestion: str = ""
    fixed: bool = False

    def format(self) -> str:
        prefix = "[FIXED]" if self.fixed else "[DRIFT]"
        text = f"{prefix} {self.kind}: {self.message}"
        if self.suggestion:
            text += f" | suggestion: {self.suggestion}"
        return text


def _iso_now() -> str:
    return datetime.now(timezone.utc).astimezone().replace(microsecond=0).isoformat()


def _load_state(session_dir: Path) -> dict:
    state_path = session_dir / "session_state.json"
    if not state_path.is_file():
        raise FileNotFoundError(f"session_state.json not found: {state_path}")
    return json.loads(state_path.read_text(encoding="utf-8"))


def _write_state_with_backup(session_dir: Path, state: dict) -> Path:
    state_path = session_dir / "session_state.json"
    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    backup = state_path.with_name(f"session_state.json.bak.{stamp}")
    shutil.copy2(state_path, backup)
    state_path.write_text(json.dumps(state, ensure_ascii=False, indent=2), encoding="utf-8")
    return backup


def _relative_to_lessons(lessons_dir: Path, path: Path) -> str:
    return path.relative_to(lessons_dir).as_posix()


def _without_version_suffix(filename: str) -> str:
    return re.sub(r"_v\d+(?=\.md$)", "", Path(filename).name)


def _candidate_paths(lessons_dir: Path, missing: str) -> list[str]:
    missing_path = Path(missing)
    lesson_id = _lesson_id_from_filename(missing)
    if not lesson_id or not lessons_dir.exists():
        return []

    if len(missing_path.parts) > 1:
        scoped = lessons_dir / missing_path.parent
        search_roots = [scoped] if scoped.exists() else []
    else:
        search_roots = [lessons_dir]

    candidates: list[Path] = []
    preferred_name = _without_version_suffix(missing)
    for root in search_roots:
        preferred = root / preferred_name
        if preferred.is_file():
            candidates.append(preferred)
        candidates.extend(sorted(root.rglob(f"{lesson_id}*.md")))

    seen: set[str] = set()
    result: list[str] = []
    for candidate in candidates:
        if not candidate.is_file():
            continue
        rel = _relative_to_lessons(lessons_dir, candidate)
        if rel not in seen:
            seen.add(rel)
            result.append(rel)
    return result


def _normalize_wait_reason(reason: str) -> str | None:
    lowered = reason.lower()
    if "answer" in lowered:
        return "awaiting_answer"
    if "grading" in lowered or "grade" in lowered:
        return "awaiting_grading"
    if "choice" in lowered or "choose" in lowered:
        return "awaiting_user_choice"
    return None


def _reconcile_wait_reason(
    state: dict,
    *,
    fix_wait_reason: bool,
) -> tuple[bool, list[ReconcileFinding]]:
    reason = state.get("wait_reason")
    if reason in VALID_WAIT_REASONS:
        return False, []

    suggestion = _normalize_wait_reason(str(reason))
    findings = [
        ReconcileFinding(
            "wait_reason",
            f"wait_reason '{reason}' is not a stable enum",
            f"move original value into wait_detail.message and set wait_reason to {suggestion!r}",
        )
    ]
    if not fix_wait_reason:
        return False, findings

    detail = state.get("wait_detail") if isinstance(state.get("wait_detail"), dict) else {}
    detail = dict(detail)
    detail.setdefault("message", reason)
    detail.setdefault("mode", state.get("current_mode"))
    lesson_match = re.search(r"L(\d+)", str(reason), re.IGNORECASE)
    if lesson_match:
        detail.setdefault("lesson_id", lesson_match.group(1).zfill(2))
    state["wait_reason"] = suggestion
    state["wait_detail"] = detail
    findings.append(
        ReconcileFinding(
            "wait_reason",
            f"normalized wait_reason to {suggestion!r}",
            "backup is written before session_state.json is updated",
            fixed=True,
        )
    )
    return True, findings


def _reconcile_variants(
    state: dict,
    lessons_dir: Path,
    *,
    fix_lesson_files: bool,
) -> tuple[bool, list[ReconcileFinding]]:
    changed = False
    findings: list[ReconcileFinding] = []
    variants = state.get("lesson_variants") or {}
    if not isinstance(variants, dict):
        return False, [ReconcileFinding("lesson_variants", "lesson_variants is not an object")]

    for lesson_id, meta in variants.items():
        if not isinstance(meta, dict):
            findings.append(ReconcileFinding("lesson_variants", f"{lesson_id} metadata is invalid"))
            continue
        active = meta.get("active")
        if not active:
            findings.append(ReconcileFinding("lesson_variants", f"{lesson_id} has no active file"))
            continue
        if _lesson_path(lessons_dir, active).is_file():
            continue

        candidates = _candidate_paths(lessons_dir, active)
        suggestion = candidates[0] if candidates else "no candidate found"
        findings.append(
            ReconcileFinding(
                "lesson_variant_active",
                f"{lesson_id} active file is missing: {active}",
                suggestion,
            )
        )
        if fix_lesson_files and candidates:
            meta["active"] = candidates[0]
            changed = True
            findings.append(
                ReconcileFinding(
                    "lesson_variant_active",
                    f"{lesson_id} active file changed to: {candidates[0]}",
                    fixed=True,
                )
            )
    return changed, findings


def _active_file_list_key(state: dict) -> str | None:
    mode = state.get("current_mode")
    if mode == "core":
        return "lesson_files_core"
    if mode == "deep":
        return "lesson_files_deep"
    if isinstance(state.get("lesson_files"), list):
        return "lesson_files"
    return None


def _reconcile_active_lesson_files(
    state: dict,
    lessons_dir: Path,
    *,
    fix_lesson_files: bool,
) -> tuple[bool, list[ReconcileFinding]]:
    files = _active_lesson_files(state)
    if not files:
        return False, []

    key = _active_file_list_key(state)
    check_through = max(state.get("current_lesson", 0), state.get("last_completed_lesson", 0))
    changed = False
    findings: list[ReconcileFinding] = []

    for index, filename in enumerate(files[:check_through]):
        if _lesson_path(lessons_dir, filename).is_file():
            continue
        candidates = _candidate_paths(lessons_dir, filename)
        suggestion = candidates[0] if candidates else "no candidate found"
        findings.append(
            ReconcileFinding(
                "lesson_file_missing",
                f"active lesson file #{index + 1} is missing: {filename}",
                suggestion,
            )
        )
        if fix_lesson_files and key and candidates:
            state[key][index] = candidates[0]
            changed = True
            findings.append(
                ReconcileFinding(
                    "lesson_file_missing",
                    f"{key}[{index}] changed to: {candidates[0]}",
                    fixed=True,
                )
            )
    return changed, findings


def reconcile_session(
    session_dir: Path,
    *,
    fix_lesson_files: bool = False,
    fix_wait_reason: bool = False,
    write_audit: bool = False,
) -> tuple[bool, list[ReconcileFinding], Path | None]:
    state = _load_state(session_dir)
    lessons_dir = session_dir / "lessons"

    changed = False
    findings: list[ReconcileFinding] = []

    step_changed, step_findings = _reconcile_wait_reason(state, fix_wait_reason=fix_wait_reason)
    changed = changed or step_changed
    findings.extend(step_findings)

    step_changed, step_findings = _reconcile_variants(
        state,
        lessons_dir,
        fix_lesson_files=fix_lesson_files,
    )
    changed = changed or step_changed
    findings.extend(step_findings)

    step_changed, step_findings = _reconcile_active_lesson_files(
        state,
        lessons_dir,
        fix_lesson_files=fix_lesson_files,
    )
    changed = changed or step_changed
    findings.extend(step_findings)

    if changed and write_audit:
        state.setdefault("state_repair_log", [])
        state["state_repair_log"].append(
            {
                "at": _iso_now(),
                "fix_lesson_files": fix_lesson_files,
                "fix_wait_reason": fix_wait_reason,
                "findings": [finding.format() for finding in findings],
            }
        )

    backup = _write_state_with_backup(session_dir, state) if changed else None
    return changed, findings, backup


def _parse_args(argv: Sequence[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Report or repair drift between session_state.json and lesson files.",
    )
    parser.add_argument("session_dir", type=Path)
    parser.add_argument("--fix-lesson-files", action="store_true")
    parser.add_argument("--fix-wait-reason", action="store_true")
    parser.add_argument("--write-audit", action="store_true")
    return parser.parse_args(list(argv))


def main(argv: Sequence[str] | None = None) -> int:
    args = _parse_args(argv if argv is not None else sys.argv[1:])
    if not args.session_dir.is_dir():
        print(f"Error: not a session directory: {args.session_dir}", file=sys.stderr)
        return 2

    try:
        changed, findings, backup = reconcile_session(
            args.session_dir,
            fix_lesson_files=args.fix_lesson_files,
            fix_wait_reason=args.fix_wait_reason,
            write_audit=args.write_audit,
        )
    except (FileNotFoundError, json.JSONDecodeError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 2

    for finding in findings:
        print(finding.format())
    if not findings:
        print("Reconcile: no drift detected")
    elif changed:
        print(f"Reconcile: repaired drift; backup: {backup}")
    else:
        print("Reconcile: drift detected; rerun with --fix-* flags to repair")

    return 0 if not findings or changed else 1


if __name__ == "__main__":
    sys.exit(main())
