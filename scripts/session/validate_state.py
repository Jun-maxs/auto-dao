#!/usr/bin/env python3
"""
validate_state.py — auto-dao session state validator

Checks the consistency between session_state.json and the actual
directory structure of a learning session. Designed to be run by
humans or CI, not by the AI model itself.

Usage:
    python scripts/session/validate_state.py <session_dir>

Example:
    python scripts/session/validate_state.py learning-history/stm32-hal_2026-04-13-09-45

Exit codes:
    0  — all checks passed
    1  — one or more checks failed
    2  — fatal error (missing files, bad JSON, etc.)
"""

import json
import re
import sys
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

# jsonschema is an optional dependency for schema validation.
# When available, it enables strict validation of session_state.json.

# ---------------------------------------------------------------------------
# Schema
# ---------------------------------------------------------------------------

_SCHEMA_PATH = Path(__file__).resolve().parents[2] / ".claude" / "skills" / "learning-engine" / "templates" / "session-state.schema.json"
with open(_SCHEMA_PATH, "r", encoding="utf-8") as f:
    _SCHEMA = json.load(f)

SCHEMA_VERSION = _SCHEMA["properties"]["schema_version"]["const"]
VALID_PHASES = set(_SCHEMA["properties"]["phase"]["enum"])
VALID_CF_MODES = set(_SCHEMA["properties"]["counterfactual_mode"]["enum"])
VALID_WAIT_REASONS = set(_SCHEMA["properties"]["wait_reason"]["enum"])
VALID_CURRENT_MODES = set(_SCHEMA["properties"]["current_mode"]["enum"])
REQUIRED_FIELDS = set(_SCHEMA["required"])


def _lesson_indices(lessons_dir: Path) -> list[int]:
    """Return sorted list of lesson indices found in lessons/ directory.

    Accepts two naming conventions:
    - Legacy:  ``lesson_N.md`` where N is an integer.
    - Current: ``NN[.X]_描述.md`` where NN is the chapter number and .X the
      optional section. Chapter number is used as the primary index; two files
      sharing a chapter (e.g. ``02.0_...md`` + ``02.1_...md``) dedupe to one
      entry.
    """
    indices: list[int] = []
    for f in lessons_dir.iterdir():
        m = re.match(r"lesson_(\d+)\.md$", f.name)
        if m:
            indices.append(int(m.group(1)))
            continue
        m = re.match(r"(\d+)(?:\.\d+)?_.*\.md$", f.name)
        if m:
            indices.append(int(m.group(1)))
    return sorted(set(indices))


def _valid_lesson_files(values: object) -> list[str]:
    """Return string lesson filenames, filtering legacy transitional nulls."""
    if not isinstance(values, list):
        return []
    return [v for v in values if isinstance(v, str) and v.strip()]


def _active_lesson_files(state: dict) -> list[str]:
    """Resolve the active lesson file list for learn/practice/deep-aware sessions."""
    current_mode = state.get("current_mode")
    if current_mode == "learn":
        files = _valid_lesson_files(state.get("lesson_files_learn"))
        if files:
            return files
    if current_mode == "practice":
        files = _valid_lesson_files(state.get("lesson_files_practice"))
        if files:
            return files
    if current_mode == "core":
        files = _valid_lesson_files(state.get("lesson_files_core"))
        if files:
            return files
    if current_mode == "deep":
        files = _valid_lesson_files(state.get("lesson_files_deep"))
        if files:
            return files
    # Legacy / compatibility path.
    return _valid_lesson_files(state.get("lesson_files"))


def _lesson_id_from_filename(filename: str) -> Optional[str]:
    """Extract leading lesson id (NN or NN.X) from a lesson filename/path."""
    name = Path(filename).name
    m = re.match(r"(\d+(?:\.\d+)?)_.*", name)
    return m.group(1) if m else None


def _lesson_path(lessons_dir: Path, filename: str) -> Path:
    """Resolve a lesson filename/path under lessons/."""
    return lessons_dir / filename


# ---------------------------------------------------------------------------
# Individual checks
# ---------------------------------------------------------------------------

class CheckResult:
    def __init__(self, name: str, passed: bool, detail: str = ""):
        self.name = name
        self.passed = passed
        self.detail = detail

    def __str__(self):
        if sys.platform == "win32":
            mark = "[PASS]" if self.passed else "[FAIL]"
        else:
            mark = "✅" if self.passed else "❌"
        msg = f"{mark} [{self.name}]"
        if self.detail:
            msg += f"  {self.detail}"
        return msg


def check_schema_version(state: dict) -> CheckResult:
    v = state.get("schema_version")
    ok = v == SCHEMA_VERSION
    return CheckResult(
        "schema_version",
        ok,
        f"expected '{SCHEMA_VERSION}', got '{v}'" if not ok else "",
    )


def check_required_fields(state: dict) -> CheckResult:
    missing = [f for f in REQUIRED_FIELDS if f not in state]
    ok = len(missing) == 0
    return CheckResult(
        "required_fields",
        ok,
        f"missing: {missing}" if not ok else "",
    )


def check_phase(state: dict) -> CheckResult:
    phase = state.get("phase")
    ok = phase in VALID_PHASES
    return CheckResult(
        "phase_valid",
        ok,
        f"'{phase}' not in {VALID_PHASES}" if not ok else "",
    )


def check_counterfactual_mode(state: dict) -> CheckResult:
    mode = state.get("counterfactual_mode")
    ok = mode in VALID_CF_MODES
    return CheckResult(
        "counterfactual_mode",
        ok,
        f"'{mode}' not in {VALID_CF_MODES}" if not ok else "",
    )


def check_wait_reason(state: dict) -> CheckResult:
    reason = state.get("wait_reason")
    ok = reason in VALID_WAIT_REASONS
    return CheckResult(
        "wait_reason",
        ok,
        f"'{reason}' not in {VALID_WAIT_REASONS}" if not ok else "",
    )


def check_current_mode(state: dict) -> CheckResult:
    """current_mode should be explicit for schema 2.3 sessions."""
    mode = state.get("current_mode")
    ok = mode in VALID_CURRENT_MODES
    return CheckResult(
        "current_mode",
        ok,
        f"'{mode}' not in {VALID_CURRENT_MODES}" if not ok else "",
    )


def _is_safe_relative_lesson_path(filename: str) -> bool:
    path = Path(filename)
    return not path.is_absolute() and ".." not in path.parts


def check_lesson_mode_paths(state: dict) -> CheckResult:
    """Lesson file lists should stay in their declared directory contract."""
    invalid: list[str] = []

    for filename in _valid_lesson_files(state.get("lesson_files_learn")):
        normalized = filename.replace("\\", "/")
        if not _is_safe_relative_lesson_path(filename):
            invalid.append(f"learn unsafe path: {filename}")
        elif not normalized.startswith("learn/"):
            invalid.append(f"learn outside lessons/learn/: {filename}")

    for filename in _valid_lesson_files(state.get("lesson_files_practice")):
        normalized = filename.replace("\\", "/")
        if not _is_safe_relative_lesson_path(filename):
            invalid.append(f"practice unsafe path: {filename}")
        elif not normalized.startswith("practice/"):
            invalid.append(f"practice outside lessons/practice/: {filename}")

    for filename in _valid_lesson_files(state.get("lesson_files_core")):
        if not _is_safe_relative_lesson_path(filename):
            invalid.append(f"core unsafe path: {filename}")
        elif not filename.replace("\\", "/").startswith("core/"):
            invalid.append(f"core outside lessons/core/: {filename}")

    for filename in _valid_lesson_files(state.get("lesson_files_deep")):
        normalized = filename.replace("\\", "/")
        if not _is_safe_relative_lesson_path(filename):
            invalid.append(f"deep unsafe path: {filename}")
        elif "/" in normalized and not normalized.startswith("deep/"):
            invalid.append(f"deep outside lessons/deep/ or legacy root: {filename}")

    return CheckResult(
        "lesson_mode_paths",
        not invalid,
        f"invalid lesson mode paths: {invalid}" if invalid else "",
    )


def check_lesson_count(state: dict, lessons_dir: Path) -> CheckResult:
    """current_lesson should be consistent with available lessons.

    When an active lesson file list is populated (learn/practice/deep/core-aware or legacy
    ``lesson_files``), ``current_lesson`` is treated as a 1-based index into
    that array and must satisfy ``0 <= current <= len(files)``.

    When absent, falls back to the legacy convention of scanning
    ``lesson_N.md`` files and checking ``current in (max_index, max_index+1)``.
    """
    lesson_files = _active_lesson_files(state)
    current = state.get("current_lesson", 0)

    if lesson_files:
        ok = 0 <= current <= len(lesson_files)
        return CheckResult(
            "lesson_count",
            ok,
            f"current_lesson={current} out of bounds 0..{len(lesson_files)}" if not ok else "",
        )

    if not lessons_dir.exists():
        if current == 0:
            return CheckResult("lesson_count", True, "no lessons dir, current_lesson=0")
        return CheckResult("lesson_count", False, "lessons/ dir missing but current_lesson > 0")

    indices = _lesson_indices(lessons_dir)
    max_index = max(indices) if indices else 0
    # current_lesson should be max_index or max_index+1 (next to generate)
    ok = current in (max_index, max_index + 1)
    return CheckResult(
        "lesson_count",
        ok,
        f"current_lesson={current}, max file index={max_index}" if not ok else "",
    )


def check_lesson_continuity(state: dict, lessons_dir: Path) -> CheckResult:
    """Lesson files should be present and consistent.

    When the active lesson file list is populated, verifies every generated
    file exists (honoring ``lesson_variants.active`` as a valid replacement).

    Otherwise falls back to legacy scanning of ``lesson_N.md`` files and
    checks they start at 1 with no duplicates.
    """
    lesson_files = _active_lesson_files(state)
    if lesson_files:
        if not lessons_dir.exists():
            return CheckResult("lesson_continuity", False, "lessons/ dir missing")
        # Only verify lessons generated so far (up to max(current_lesson, last_completed)).
        # Future planned lessons are expected to be missing during progression.
        current = state.get("current_lesson", 0)
        last = state.get("last_completed_lesson", 0)
        check_through = max(current, last)
        variants = state.get("lesson_variants") or {}
        truly_missing: list[str] = []
        for fname in lesson_files[:check_through]:
            if _lesson_path(lessons_dir, fname).exists():
                continue
            lesson_id = _lesson_id_from_filename(fname)
            if lesson_id:
                active = variants.get(lesson_id, {}).get("active")
                if active and _lesson_path(lessons_dir, active).exists():
                    continue
            truly_missing.append(fname)
        ok = len(truly_missing) == 0
        return CheckResult(
            "lesson_continuity",
            ok,
            f"missing lesson files through index {check_through} (variants checked): {truly_missing}" if not ok else "",
        )

    if not lessons_dir.exists():
        return CheckResult("lesson_continuity", True, "no lessons dir")
    indices = _lesson_indices(lessons_dir)
    if not indices:
        return CheckResult("lesson_continuity", True, "no lesson files")
    # Allow gaps due to remedial/branch lessons (lesson_N_remedial.md, lesson_N_branch.md)
    # Check: sorted, unique, starts at 1
    ok = indices == sorted(set(indices)) and indices[0] == 1
    return CheckResult(
        "lesson_continuity",
        ok,
        f"indices must start at 1 and be unique, got {indices}" if not ok else "",
    )


def check_completed_has_report(state: dict, session_dir: Path) -> CheckResult:
    """If phase is 'completed', report.md should exist."""
    phase = state.get("phase")
    if phase != "completed":
        return CheckResult("completed_report", True, "phase != completed, skipped")
    report = session_dir / "report.md"
    ok = report.exists()
    return CheckResult(
        "completed_report",
        ok,
        "phase=completed but report.md missing" if not ok else "",
    )


def check_mastery_rate(state: dict) -> CheckResult:
    """mastery_rate should equal passed/(passed+failed) if there are attempts."""
    passed = state.get("mastery_passed", 0)
    failed = state.get("mastery_failed", 0)
    rate = state.get("mastery_rate", 0.0)
    total = passed + failed
    if total == 0:
        ok = rate == 0.0
        return CheckResult("mastery_rate", ok, f"no attempts but rate={rate}" if not ok else "")
    expected = round(passed / total, 4)
    actual = round(rate, 4)
    ok = abs(expected - actual) < 0.01
    return CheckResult(
        "mastery_rate",
        ok,
        f"expected ~{expected}, got {actual}" if not ok else "",
    )


def _resolve_lesson_file(state: dict, check_index: int) -> Optional[str]:
    """Resolve the on-disk filename for a given 1-based lesson index.

    Preference order:
    1. The active mode-specific lesson list entry from state, then checked against
       ``lesson_variants[<lesson_id>].active`` (lesson_id extracted as the
       leading NN[.X] prefix of the filename) — if a variant is active, it
       overrides the base lesson_files entry.
    2. Legacy ``lesson_{check_index}.md``.

    Returns None if nothing can be resolved.
    """
    lesson_files = _active_lesson_files(state)
    if 0 < check_index <= len(lesson_files):
        base = lesson_files[check_index - 1]
        variants = state.get("lesson_variants") or {}
        lesson_id = _lesson_id_from_filename(base)
        if lesson_id:
            active = variants.get(lesson_id, {}).get("active")
            if active:
                return active
        return base
    return None


def check_learning_has_lesson(state: dict, lessons_dir: Path) -> CheckResult:
    """If phase='learning' and current_lesson > 0, that lesson file should exist."""
    phase = state.get("phase")
    current = state.get("current_lesson", 0)
    if phase != "learning" or current == 0:
        return CheckResult("learning_has_lesson", True, "skipped (phase or lesson 0)")
    # The file for the current lesson being worked on (or last generated)
    last = state.get("last_completed_lesson", 0)
    check_index = max(current, last)
    if check_index == 0:
        return CheckResult("learning_has_lesson", True, "no lessons yet")

    resolved = _resolve_lesson_file(state, check_index)
    if resolved is not None:
        target = _lesson_path(lessons_dir, resolved)
        ok = target.exists()
        return CheckResult(
            "learning_has_lesson",
            ok,
            f"{resolved} missing" if not ok else "",
        )

    # Fallback: legacy convention
    target = lessons_dir / f"lesson_{check_index}.md"
    ok = target.exists()
    return CheckResult(
        "learning_has_lesson",
        ok,
        f"lesson_{check_index}.md missing" if not ok else "",
    )


def check_lesson_variants_active(state: dict, lessons_dir: Path) -> CheckResult:
    """Every declared lesson variant active file should exist."""
    variants = state.get("lesson_variants") or {}
    if not variants:
        return CheckResult("lesson_variants_active", True, "no variants")
    missing = []
    for lesson_id, meta in variants.items():
        if not isinstance(meta, dict):
            missing.append(f"{lesson_id}: invalid metadata")
            continue
        active = meta.get("active")
        if not active:
            missing.append(f"{lesson_id}: active missing")
            continue
        if not _lesson_path(lessons_dir, active).exists():
            missing.append(f"{lesson_id}: {active}")
    return CheckResult(
        "lesson_variants_active",
        not missing,
        f"missing active variant files: {missing}" if missing else "",
    )


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def validate(session_dir: Path) -> list[CheckResult]:
    state_file = session_dir / "session_state.json"
    lessons_dir = session_dir / "lessons"

    if not state_file.exists():
        return [CheckResult("file_exists", False, f"{state_file} not found")]

    try:
        with open(state_file, "r", encoding="utf-8") as f:
            state = json.load(f)
    except json.JSONDecodeError as e:
        return [CheckResult("json_parse", False, str(e))]

    results = [
        check_schema_version(state),
        check_required_fields(state),
        check_phase(state),
        check_counterfactual_mode(state),
        check_wait_reason(state),
        check_current_mode(state),
        check_lesson_mode_paths(state),
        check_lesson_count(state, lessons_dir),
        check_lesson_continuity(state, lessons_dir),
        check_completed_has_report(state, session_dir),
        check_mastery_rate(state),
        check_learning_has_lesson(state, lessons_dir),
        check_lesson_variants_active(state, lessons_dir),
    ]
    return results


def main():
    if len(sys.argv) < 2:
        print(f"Usage: {sys.argv[0]} <session_dir>", file=sys.stderr)
        sys.exit(2)

    session_dir = Path(sys.argv[1])
    if not session_dir.is_dir():
        print(f"Error: '{session_dir}' is not a directory", file=sys.stderr)
        sys.exit(2)

    results = validate(session_dir)

    passed = sum(1 for r in results if r.passed)
    total = len(results)

    for r in results:
        print(r)
    print(f"\n{'=' * 40}")
    print(f"Result: {passed}/{total} checks passed")

    sys.exit(0 if passed == total else 1)


if __name__ == "__main__":
    main()
