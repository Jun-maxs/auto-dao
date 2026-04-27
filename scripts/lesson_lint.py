#!/usr/bin/env python3
"""Machine-check lesson contracts for generated Markdown lessons.

The linter intentionally starts small: it turns the highest-risk teaching
rules into deterministic checks that can run after lesson generation and in CI.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Iterable, Sequence


def _ensure_utf8_stdio() -> None:
    """Avoid UnicodeEncodeError for Chinese lesson titles on Windows consoles."""
    for stream in (sys.stdout, sys.stderr):
        encoding = getattr(stream, "encoding", "") or ""
        if encoding.lower() in ("utf-8", "utf8"):
            continue
        try:
            stream.reconfigure(encoding="utf-8")  # type: ignore[attr-defined]
        except Exception:
            pass


_ensure_utf8_stdio()


FENCE_RE = re.compile(r"^\s*(```+|~~~+)")
PLACEHOLDER_RE = re.compile(r"\{([^{}\n]{1,100})\}")
IMAGE_RE = re.compile(
    r"!\[[^\]]*\]\((?P<target>[^)\s]+)(?:\s+\"[^\"]*\")?\)"
)

FILE_DRIVEN_VIOLATIONS = (
    "直接发给我",
    "发给我",
    "聊天里回答",
    "在聊天里回答",
    "对话中回答",
    "在对话中回答",
    "回复给我",
    "直接回复",
    "直接按编号回答",
    "按编号回答即可",
    "把答案发在聊天",
)

KNOWN_PLACEHOLDER_NAMES = {
    "caption",
    "hash",
    "image_hash",
    "lesson_stem",
    "session_dir",
    "source_path",
    "topic",
    "topic_id",
}

CORE_STRUCTURE_RULES = (
    ("core_faq", ("FAQ", "开篇先问", "常见问题")),
    ("core_first_act", ("第一幕",)),
    ("core_mid_check", ("Mid-check", "Mid check", "先停一下", "自检")),
    ("core_exit", ("出口检查题", "Next-step menu", "下一步", "检查题")),
)

LEARN_STRUCTURE_RULES = (
    ("learn_guess", ("先猜一下",)),
    ("learn_mental_model", ("一句话心智模型",)),
    ("learn_minimal_example", ("看一个最小例子",)),
    ("learn_anchor_points", ("三个关键锚点",)),
    ("learn_hard_lesson", ("血的教训",)),
    ("learn_restate", ("80 字复述", "80字复述")),
)

LEARN_FORBIDDEN_MARKERS = (
    (
        "learn_no_generator_state",
        ("concept_tags", "session_state", "lesson_files", "current_mode"),
    ),
    (
        "learn_no_source_coverage_table",
        ("源文覆盖表", "源文位置", "本课落点", "必须掌握到什么程度"),
    ),
    (
        "learn_no_deep_feedback_sections",
        ("## 掌握度反馈", "## Reflection", "## 七、思考模块"),
    ),
    ("learn_no_appendix", ("## 附录", "### 附录")),
)

PRACTICE_STRUCTURE_RULES = (
    ("practice_retrieval", ("检索题",)),
    ("practice_transfer", ("迁移题",)),
    ("practice_correction", ("改错题",)),
    ("practice_feedback", ("批改反馈",)),
)

DEEP_SOURCE_MARKERS = (
    "资料原文",
    "本节参考",
    "来源：",
    "参考：",
    "Source:",
    "Sources:",
    "References",
)

DEEP_B_REQUIRED_MARKERS = (
    ("deep_b_scenario_closures", ("scenario_closures",)),
    ("deep_b_notes_dir", ("notes_dir", "_notes/", "my_notes.md")),
    ("deep_b_photos", ("photos", "拍照")),
    ("deep_b_exercises", ("exercises", "练习")),
)


@dataclass(frozen=True)
class LintIssue:
    path: str
    line: int
    rule: str
    message: str
    severity: str = "error"

    def format(self) -> str:
        location = f"{self.path}:{self.line}" if self.line else self.path
        return f"{location}: {self.severity}: {self.rule}: {self.message}"


def infer_lesson_kind(path: Path) -> str:
    parts = {part.lower() for part in path.parts}
    if "learn" in parts:
        return "learn"
    if "practice" in parts:
        return "practice"
    if "core" in parts:
        return "core"
    if "deep" in parts:
        return "deep"
    return "legacy"


def _non_code_lines(lines: Sequence[str]) -> Iterable[tuple[int, str]]:
    in_code = False
    fence_char = ""
    for lineno, line in enumerate(lines, 1):
        fence = FENCE_RE.match(line)
        if fence:
            marker = fence.group(1)
            if not in_code:
                in_code = True
                fence_char = marker[0]
            elif marker[0] == fence_char:
                in_code = False
                fence_char = ""
            continue
        if not in_code:
            yield lineno, line


def _is_allowed_placeholder(inner: str) -> bool:
    stripped = inner.strip()
    if not stripped:
        return True
    if re.fullmatch(r"[_\s]+", inner):
        return True
    if stripped.startswith(("#", ":")):
        return True
    if stripped in KNOWN_PLACEHOLDER_NAMES:
        return False
    # Named template placeholders are usually snake/kebab identifiers.
    # Math sets and formulas also use braces, so avoid flagging free-form
    # Chinese terms, units, addresses, or expressions such as {n-1}.
    if re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", stripped) and "_" in stripped:
        return False
    if re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*-[A-Za-z][A-Za-z0-9_-]*", stripped):
        return False
    if re.fullmatch(r"[a-z][a-z0-9]{3,}", stripped):
        return False
    if not re.search(r"[A-Za-z_\u4e00-\u9fff]", stripped):
        return True
    return True


def _is_external_target(target: str) -> bool:
    lowered = target.lower()
    return lowered.startswith(("http://", "https://", "//", "data:", "mailto:", "#"))


def _expected_image_prefix(path: Path) -> str | None:
    parent = path.parent.name.lower()
    if parent in {"learn", "practice", "core", "deep"}:
        return "../../images/"
    if parent == "lessons":
        return "../images/"
    return None


def _contains_any(content: str, needles: Sequence[str]) -> bool:
    return any(needle in content for needle in needles)


def _find_first_line(content: str, needles: Sequence[str]) -> int:
    for lineno, line in enumerate(content.splitlines(), 1):
        if any(needle in line for needle in needles):
            return lineno
    return 1


def _is_deep_b_lesson(content: str) -> bool:
    return (
        "scenario_closures" in content
        or "teaching_mode: B" in content
        or "teaching_mode = B" in content
        or "模式 B" in content
    )


def check_placeholders(path: Path, lines: Sequence[str]) -> list[LintIssue]:
    issues: list[LintIssue] = []
    for lineno, line in _non_code_lines(lines):
        for match in PLACEHOLDER_RE.finditer(line):
            inner = match.group(1)
            if _is_allowed_placeholder(inner):
                continue
            issues.append(
                LintIssue(
                    str(path),
                    lineno,
                    "unresolved_placeholder",
                    f"named placeholder '{{{inner}}}' remains in lesson text",
                )
            )
    return issues


def check_file_driven(path: Path, lines: Sequence[str]) -> list[LintIssue]:
    issues: list[LintIssue] = []
    for lineno, line in _non_code_lines(lines):
        for phrase in sorted(FILE_DRIVEN_VIOLATIONS, key=len, reverse=True):
            if phrase in line:
                issues.append(
                    LintIssue(
                        str(path),
                        lineno,
                        "file_driven_protocol",
                        f"replace chat-style answer request '{phrase}' with an answers/notes file workflow",
                    )
                )
                break
    return issues


def check_image_paths(path: Path, lines: Sequence[str]) -> list[LintIssue]:
    expected = _expected_image_prefix(path)
    if expected is None:
        return []

    issues: list[LintIssue] = []
    for lineno, line in _non_code_lines(lines):
        for match in IMAGE_RE.finditer(line):
            target = match.group("target").strip("<>")
            if _is_external_target(target) or "images/" not in target.replace("\\", "/"):
                continue
            normalized = target.replace("\\", "/")
            if not normalized.startswith(expected):
                issues.append(
                    LintIssue(
                        str(path),
                        lineno,
                        "image_path_contract",
                        f"image path '{target}' should start with '{expected}' from this lesson location",
                    )
                )
    return issues


def check_core_structure(path: Path, content: str, kind: str) -> list[LintIssue]:
    if kind != "core":
        return []

    issues: list[LintIssue] = []
    for rule, markers in CORE_STRUCTURE_RULES:
        if _contains_any(content, markers):
            continue
        issues.append(
            LintIssue(
                str(path),
                1,
                rule,
                f"core lesson is missing one of: {', '.join(markers)}",
            )
        )
    return issues


def check_learn_contract(path: Path, content: str, kind: str) -> list[LintIssue]:
    if kind != "learn":
        return []

    issues: list[LintIssue] = []
    for rule, markers in LEARN_STRUCTURE_RULES:
        if _contains_any(content, markers):
            continue
        issues.append(
            LintIssue(
                str(path),
                1,
                rule,
                f"learn-card is missing one of: {', '.join(markers)}",
            )
        )

    for rule, markers in LEARN_FORBIDDEN_MARKERS:
        if not _contains_any(content, markers):
            continue
        issues.append(
            LintIssue(
                str(path),
                _find_first_line(content, markers),
                rule,
                f"learn-card should keep learner-facing content only; remove: {', '.join(markers)}",
            )
        )
    return issues


def check_practice_contract(path: Path, content: str, kind: str) -> list[LintIssue]:
    if kind != "practice":
        return []

    issues: list[LintIssue] = []
    for rule, markers in PRACTICE_STRUCTURE_RULES:
        if _contains_any(content, markers):
            continue
        issues.append(
            LintIssue(
                str(path),
                1,
                rule,
                f"practice pack is missing one of: {', '.join(markers)}",
            )
        )
    return issues


def check_deep_contract(path: Path, content: str, kind: str) -> list[LintIssue]:
    if kind != "deep":
        return []

    issues: list[LintIssue] = []
    if not _contains_any(content, DEEP_SOURCE_MARKERS):
        issues.append(
            LintIssue(
                str(path),
                1,
                "deep_source_marker",
                "deep lesson should preserve source markers or section-level references",
            )
        )

    if _is_deep_b_lesson(content):
        for rule, markers in DEEP_B_REQUIRED_MARKERS:
            if _contains_any(content, markers):
                continue
            issues.append(
                LintIssue(
                    str(path),
                    1,
                    rule,
                    f"B-mode deep lesson is missing one of: {', '.join(markers)}",
                )
            )
    return issues


def check_code_block_lengths(
    path: Path,
    lines: Sequence[str],
    kind: str,
    *,
    max_core_lines: int,
    max_learn_lines: int,
    max_practice_lines: int,
    max_deep_lines: int,
) -> list[LintIssue]:
    max_lines_by_kind = {
        "core": max_core_lines,
        "learn": max_learn_lines,
        "practice": max_practice_lines,
        "deep": max_deep_lines,
        "legacy": max_deep_lines,
    }
    max_lines = max_lines_by_kind.get(kind, max_deep_lines)
    if kind in {"core", "learn", "practice"}:
        rule = f"{kind}_code_block_length"
    else:
        rule = "deep_code_block_length"
    issues: list[LintIssue] = []

    in_code = False
    fence_char = ""
    start_line = 0
    code_lines = 0

    for lineno, line in enumerate(lines, 1):
        fence = FENCE_RE.match(line)
        if fence:
            marker = fence.group(1)
            if not in_code:
                in_code = True
                fence_char = marker[0]
                start_line = lineno
                code_lines = 0
            elif marker[0] == fence_char:
                if code_lines > max_lines:
                    issues.append(
                        LintIssue(
                            str(path),
                            start_line,
                            rule,
                            f"code block has {code_lines} lines; limit is {max_lines}",
                        )
                    )
                in_code = False
                fence_char = ""
                start_line = 0
                code_lines = 0
            continue

        if in_code:
            code_lines += 1

    if in_code and code_lines > max_lines:
        issues.append(
            LintIssue(
                str(path),
                start_line,
                rule,
                f"unterminated code block has {code_lines} lines; limit is {max_lines}",
            )
        )

    return issues


def lint_markdown_file(
    path: Path,
    *,
    mode: str = "auto",
    max_core_code_lines: int = 15,
    max_learn_code_lines: int = 25,
    max_practice_code_lines: int = 40,
    max_deep_code_lines: int = 60,
) -> list[LintIssue]:
    content = path.read_text(encoding="utf-8")
    lines = content.splitlines()
    kind = infer_lesson_kind(path) if mode == "auto" else mode

    issues: list[LintIssue] = []
    issues.extend(check_placeholders(path, lines))
    issues.extend(check_file_driven(path, lines))
    issues.extend(check_image_paths(path, lines))
    issues.extend(check_core_structure(path, content, kind))
    issues.extend(check_learn_contract(path, content, kind))
    issues.extend(check_practice_contract(path, content, kind))
    issues.extend(check_deep_contract(path, content, kind))
    issues.extend(
        check_code_block_lengths(
            path,
            lines,
            kind,
            max_core_lines=max_core_code_lines,
            max_learn_lines=max_learn_code_lines,
            max_practice_lines=max_practice_code_lines,
            max_deep_lines=max_deep_code_lines,
        )
    )
    return issues


def collect_markdown_files(paths: Sequence[Path]) -> list[Path]:
    files: list[Path] = []
    for path in paths:
        if path.is_file():
            if path.suffix.lower() == ".md":
                files.append(path)
            continue
        if not path.is_dir():
            raise FileNotFoundError(f"Path not found: {path}")

        scan_root = path / "lessons" if (path / "session_state.json").exists() else path
        if not scan_root.exists():
            continue
        files.extend(sorted(p for p in scan_root.rglob("*.md") if p.is_file()))
    return sorted(dict.fromkeys(files))


def _parse_args(argv: Sequence[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Lint generated lesson Markdown against auto-tutor lesson contracts.",
    )
    parser.add_argument("paths", nargs="+", type=Path, help="Lesson file(s) or session/directories to lint")
    parser.add_argument("--mode", choices=["auto", "learn", "practice", "core", "deep", "legacy"], default="auto")
    parser.add_argument("--format", choices=["text", "json"], default="text")
    parser.add_argument("--max-core-code-lines", type=int, default=15)
    parser.add_argument("--max-learn-code-lines", type=int, default=25)
    parser.add_argument("--max-practice-code-lines", type=int, default=40)
    parser.add_argument("--max-deep-code-lines", type=int, default=60)
    return parser.parse_args(list(argv))


def main(argv: Sequence[str] | None = None) -> int:
    args = _parse_args(argv if argv is not None else sys.argv[1:])
    try:
        files = collect_markdown_files(args.paths)
    except FileNotFoundError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 2

    issues: list[LintIssue] = []
    for file in files:
        issues.extend(
            lint_markdown_file(
                file,
                mode=args.mode,
                max_core_code_lines=args.max_core_code_lines,
                max_learn_code_lines=args.max_learn_code_lines,
                max_practice_code_lines=args.max_practice_code_lines,
                max_deep_code_lines=args.max_deep_code_lines,
            )
        )

    if args.format == "json":
        print(json.dumps([asdict(issue) for issue in issues], ensure_ascii=False, indent=2))
    else:
        for issue in issues:
            print(issue.format())
        print(f"Lesson lint: {len(files)} file(s), {len(issues)} issue(s)")

    return 1 if issues else 0


if __name__ == "__main__":
    sys.exit(main())
