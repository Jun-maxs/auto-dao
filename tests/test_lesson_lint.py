"""Tests for scripts/lesson_lint.py."""

from __future__ import annotations

from pathlib import Path

from scripts.lesson_lint import collect_markdown_files, lint_markdown_file, main


def _write_core(path: Path, extra: str = "") -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        "\n".join(
            [
                "# 01 Core",
                "",
                "## FAQ",
                "",
                "1. **Q: 为什么要学它？**",
                "",
                "## 第一幕：为什么需要这个机制？",
                "",
                "这里有一张图：![demo](../../images/demo.png)",
                "",
                "## Mid-check",
                "",
                "请你默答三个问题。",
                "",
                "## 你现在先完成 3 个检查题",
                "",
                "请把答案写入 `answers/01_core.md`，系统会读取文件批改。",
                "",
                extra,
            ]
        ),
        encoding="utf-8",
    )
    return path


def _write_learn(path: Path, extra: str = "") -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        "\n".join(
            [
                "# 01 Learn：为什么要先做最小例子？",
                "",
                "**建议用时**：10 分钟",
                "**学完你能做什么**：能独立改一个参数",
                "",
                "## 1. 先猜一下",
                "",
                "如果直接改大工程，哪里最容易错？",
                "",
                "## 2. 一句话心智模型",
                "",
                "**先让一个最小例子跑通，再迁移到真实项目。**",
                "",
                "## 3. 最小机制",
                "",
                "只讲输入、输出和失败后果。",
                "",
                "## 4. 看一个最小例子",
                "",
                "```python",
                "value = 1",
                "print(value)",
                "```",
                "",
                "**三个关键锚点**：",
                "",
                "| 锚点 | 为什么重要 | 写错会怎样 |",
                "|------|------------|------------|",
                "| `value` | 入口最小 | 难定位问题 |",
                "",
                "这里有一张图：![demo](../../images/demo.png)",
                "",
                "## 5. 血的教训",
                "",
                "常见错法：还没确认输入就改全局配置。",
                "",
                "## 6. 你来做",
                "",
                "请把答案写入本文件的答案区。",
                "",
                "## 7. 80 字复述",
                "",
                "用自己的话解释这个流程。",
                "",
                extra,
            ]
        ),
        encoding="utf-8",
    )
    return path


def _write_practice(path: Path, extra: str = "") -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        "\n".join(
            [
                "# 01 Learn · 练习包",
                "",
                "## A. 检索题",
                "",
                "写出最小例子的第一步。",
                "",
                "## B. 迁移题",
                "",
                "把这个流程迁移到另一个文件。",
                "",
                "## C. 改错题",
                "",
                "指出这段流程错在哪里。",
                "",
                "## 批改反馈",
                "",
                "AI 批改后追加到这里。",
                "",
                extra,
            ]
        ),
        encoding="utf-8",
    )
    return path


class TestLessonLintHappyPath:
    def test_good_core_lesson_passes(self, tmp_path: Path):
        lesson = _write_core(tmp_path / "session" / "lessons" / "core" / "01_core.md")
        issues = lint_markdown_file(lesson)
        assert issues == []

    def test_good_learn_lesson_passes(self, tmp_path: Path):
        lesson = _write_learn(tmp_path / "session" / "lessons" / "learn" / "01_learn.learn.md")
        issues = lint_markdown_file(lesson)
        assert issues == []

    def test_good_practice_pack_passes(self, tmp_path: Path):
        lesson = _write_practice(
            tmp_path / "session" / "lessons" / "practice" / "01_learn.practice.md"
        )
        issues = lint_markdown_file(lesson)
        assert issues == []

    def test_collect_session_scans_lessons_only(self, tmp_path: Path):
        session = tmp_path / "session"
        session.mkdir()
        (session / "session_state.json").write_text("{}", encoding="utf-8")
        lesson = _write_core(session / "lessons" / "core" / "01_core.md")
        (session / "notes.md").write_text("{placeholder}", encoding="utf-8")

        assert collect_markdown_files([session]) == [lesson]


class TestLessonLintRules:
    def test_named_placeholder_fails_but_fill_blank_passes(self, tmp_path: Path):
        lesson = _write_core(
            tmp_path / "session" / "lessons" / "core" / "01_core.md",
            extra="这里还残留 {concept_tags}，但这个填空 {_____} 可以保留。",
        )

        issues = lint_markdown_file(lesson)
        assert [issue.rule for issue in issues] == ["unresolved_placeholder"]
        assert "{concept_tags}" in issues[0].message

    def test_formula_braces_do_not_count_as_placeholders(self, tmp_path: Path):
        lesson = _write_core(
            tmp_path / "session" / "lessons" / "core" / "01_core.md",
            extra="公式可以写成 {n-1}、{0xAA, 0xBB}、{有效地址}。",
        )

        issues = lint_markdown_file(lesson)
        assert issues == []

    def test_chat_style_answer_request_fails(self, tmp_path: Path):
        lesson = _write_core(
            tmp_path / "session" / "lessons" / "core" / "01_core.md",
            extra="你直接按编号回答即可。",
        )

        issues = lint_markdown_file(lesson)
        assert any(issue.rule == "file_driven_protocol" for issue in issues)

    def test_core_image_path_must_point_two_levels_up(self, tmp_path: Path):
        lesson = _write_core(
            tmp_path / "session" / "lessons" / "core" / "01_core.md",
            extra="![bad](../images/wrong.png)",
        )

        issues = lint_markdown_file(lesson)
        assert any(issue.rule == "image_path_contract" for issue in issues)

    def test_core_structure_is_required(self, tmp_path: Path):
        lesson = tmp_path / "session" / "lessons" / "core" / "01_core.md"
        lesson.parent.mkdir(parents=True)
        lesson.write_text("# Missing structure\n", encoding="utf-8")

        issues = lint_markdown_file(lesson)
        rules = {issue.rule for issue in issues}
        assert {"core_faq", "core_first_act", "core_mid_check", "core_exit"} <= rules

    def test_learn_structure_is_required(self, tmp_path: Path):
        lesson = tmp_path / "session" / "lessons" / "learn" / "01_learn.learn.md"
        lesson.parent.mkdir(parents=True)
        lesson.write_text("# Missing learn structure\n", encoding="utf-8")

        issues = lint_markdown_file(lesson)
        rules = {issue.rule for issue in issues}
        assert {
            "learn_guess",
            "learn_mental_model",
            "learn_minimal_example",
            "learn_anchor_points",
            "learn_hard_lesson",
            "learn_restate",
        } <= rules

    def test_learn_lesson_rejects_deep_or_generator_residue(self, tmp_path: Path):
        lesson = _write_learn(
            tmp_path / "session" / "lessons" / "learn" / "01_learn.learn.md",
            extra="\n".join(
                [
                    "concept_tags: [demo]",
                    "## 源文覆盖表",
                    "| 源文位置 | 本课落点 |",
                    "## 掌握度反馈",
                    "## 附录",
                ]
            ),
        )

        issues = lint_markdown_file(lesson)
        rules = {issue.rule for issue in issues}
        assert {
            "learn_no_generator_state",
            "learn_no_source_coverage_table",
            "learn_no_deep_feedback_sections",
            "learn_no_appendix",
        } <= rules

    def test_learn_image_path_must_point_two_levels_up(self, tmp_path: Path):
        lesson = _write_learn(
            tmp_path / "session" / "lessons" / "learn" / "01_learn.learn.md",
            extra="![bad](../images/wrong.png)",
        )

        issues = lint_markdown_file(lesson)
        assert any(issue.rule == "image_path_contract" for issue in issues)

    def test_practice_structure_is_required(self, tmp_path: Path):
        lesson = tmp_path / "session" / "lessons" / "practice" / "01_learn.practice.md"
        lesson.parent.mkdir(parents=True)
        lesson.write_text("# Missing practice structure\n", encoding="utf-8")

        issues = lint_markdown_file(lesson)
        rules = {issue.rule for issue in issues}
        assert {
            "practice_retrieval",
            "practice_transfer",
            "practice_correction",
            "practice_feedback",
        } <= rules

    def test_core_code_block_length_is_limited(self, tmp_path: Path):
        code = "\n".join(f"line {i}" for i in range(16))
        lesson = _write_core(
            tmp_path / "session" / "lessons" / "core" / "01_core.md",
            extra=f"```c\n{code}\n```",
        )

        issues = lint_markdown_file(lesson)
        assert any(issue.rule == "core_code_block_length" for issue in issues)

    def test_learn_code_block_length_is_limited(self, tmp_path: Path):
        code = "\n".join(f"line {i}" for i in range(26))
        lesson = _write_learn(
            tmp_path / "session" / "lessons" / "learn" / "01_learn.learn.md",
            extra=f"```python\n{code}\n```",
        )

        issues = lint_markdown_file(lesson)
        assert any(issue.rule == "learn_code_block_length" for issue in issues)

    def test_deep_lesson_requires_source_marker(self, tmp_path: Path):
        lesson = tmp_path / "session" / "lessons" / "deep" / "01_deep.md"
        lesson.parent.mkdir(parents=True)
        lesson.write_text("# Deep\n\n没有来源标注。\n", encoding="utf-8")

        issues = lint_markdown_file(lesson)
        assert any(issue.rule == "deep_source_marker" for issue in issues)

    def test_cli_returns_nonzero_on_issues(self, tmp_path: Path):
        lesson = _write_core(
            tmp_path / "session" / "lessons" / "core" / "01_core.md",
            extra="{concept_tags}",
        )

        assert main([str(lesson)]) == 1
