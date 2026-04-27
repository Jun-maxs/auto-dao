"""Tests for scripts/session/validate_state.py"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from scripts.session.validate_state import (
    check_schema_version,
    check_required_fields,
    check_phase,
    check_counterfactual_mode,
    check_wait_reason,
    check_current_mode,
    check_lesson_mode_paths,
    check_lesson_count,
    check_lesson_continuity,
    check_completed_has_report,
    check_mastery_rate,
    check_learning_has_lesson,
    check_lesson_variants_active,
    VALID_PHASES,
    VALID_CF_MODES,
    VALID_WAIT_REASONS,
    VALID_CURRENT_MODES,
)


class TestCheckSchemaVersion:
    def test_valid(self):
        state = {"schema_version": "2.3"}
        result = check_schema_version(state)
        assert result.passed

    def test_invalid(self):
        state = {"schema_version": "1.0"}
        result = check_schema_version(state)
        assert not result.passed

    def test_old_version_rejected(self):
        # 2.0/2.1/2.2 were prior schemas without the complete core/deep fields.
        # After 2.3 is declared canonical, older versions must be flagged for migration.
        state = {"schema_version": "2.0"}
        result = check_schema_version(state)
        assert not result.passed

    def test_missing(self):
        state = {}
        result = check_schema_version(state)
        assert not result.passed


class TestCheckRequiredFields:
    def test_all_present(self):
        state = {
            "schema_version": "2.3",
            "topic_id": "test",
            "source_path": "test.pdf",
            "phase": "learning",
            "current_lesson": 1,
            "total_lessons": 5,
            "created_at": "2026-01-01T00:00:00+08:00",
            "updated_at": "2026-01-01T00:00:00+08:00",
        }
        result = check_required_fields(state)
        assert result.passed

    def test_missing_fields(self):
        state = {"schema_version": "2.3", "topic_id": "test"}
        result = check_required_fields(state)
        assert not result.passed
        assert len(result.detail) > 0


class TestCheckPhase:
    def test_valid_phases(self):
        for phase in VALID_PHASES:
            result = check_phase({"phase": phase})
            assert result.passed, f"phase '{phase}' should be valid"

    def test_invalid_phase(self):
        result = check_phase({"phase": "invalid"})
        assert not result.passed

    def test_missing_phase(self):
        result = check_phase({})
        assert not result.passed


class TestCheckCounterfactualMode:
    def test_valid_modes(self):
        for mode in VALID_CF_MODES:
            result = check_counterfactual_mode({"counterfactual_mode": mode})
            assert result.passed, f"mode '{mode}' should be valid"

    def test_invalid_mode(self):
        result = check_counterfactual_mode({"counterfactual_mode": "yes"})
        assert not result.passed


class TestCheckWaitReason:
    def test_valid_reasons(self):
        for reason in VALID_WAIT_REASONS:
            result = check_wait_reason({"wait_reason": reason})
            assert result.passed, f"reason '{reason}' should be valid"

    def test_invalid_reason(self):
        result = check_wait_reason({"wait_reason": "invalid"})
        assert not result.passed


class TestCheckCurrentMode:
    def test_valid_modes(self):
        for mode in VALID_CURRENT_MODES:
            result = check_current_mode({"current_mode": mode})
            assert result.passed, f"mode '{mode}' should be valid"

    def test_invalid_mode(self):
        result = check_current_mode({"current_mode": "compact"})
        assert not result.passed

    def test_missing_mode(self):
        result = check_current_mode({})
        assert not result.passed


class TestCheckLessonModePaths:
    def test_core_and_deep_paths_valid(self):
        state = {
            "lesson_files_learn": ["learn/01_learn.md"],
            "lesson_files_practice": ["practice/01_practice.md"],
            "lesson_files_core": ["core/01_core.md"],
            "lesson_files_deep": ["deep/01_deep.md", "02_legacy_deep.md"],
        }
        result = check_lesson_mode_paths(state)
        assert result.passed, result.detail

    def test_learn_must_live_under_learn_dir(self):
        result = check_lesson_mode_paths({"lesson_files_learn": ["01_learn.md"]})
        assert not result.passed
        assert "lessons/learn" in result.detail

    def test_practice_must_live_under_practice_dir(self):
        result = check_lesson_mode_paths({"lesson_files_practice": ["learn/01_wrong.md"]})
        assert not result.passed
        assert "lessons/practice" in result.detail

    def test_core_must_live_under_core_dir(self):
        result = check_lesson_mode_paths({"lesson_files_core": ["01_core.md"]})
        assert not result.passed
        assert "lessons/core" in result.detail

    def test_deep_allows_only_deep_dir_or_legacy_root(self):
        result = check_lesson_mode_paths({"lesson_files_deep": ["core/01_wrong.md"]})
        assert not result.passed
        assert "lessons/deep" in result.detail

    def test_parent_traversal_rejected(self):
        result = check_lesson_mode_paths({"lesson_files_core": ["core/../01_core.md"]})
        assert not result.passed
        assert "unsafe" in result.detail


class TestCheckLessonContinuity:
    def test_empty_dir(self, tmp_path: Path):
        result = check_lesson_continuity({}, tmp_path)
        assert result.passed

    def test_no_lesson_files(self, tmp_path: Path):
        # Create a non-lesson file
        (tmp_path / "summary.md").touch()
        result = check_lesson_continuity({}, tmp_path)
        assert result.passed  # No lesson files means trivially continuous

    def test_consecutive_lessons(self, tmp_path: Path):
        (tmp_path / "lesson_1.md").touch()
        (tmp_path / "lesson_2.md").touch()
        (tmp_path / "lesson_3.md").touch()
        result = check_lesson_continuity({}, tmp_path)
        assert result.passed

    def test_missing_lesson(self, tmp_path: Path):
        # Remedial/branch lessons may create gaps (lesson_N_remedial.md, lesson_N_branch.md)
        # The implementation intentionally allows gaps — only unique ascending order is checked
        (tmp_path / "lesson_1.md").touch()
        (tmp_path / "lesson_3.md").touch()  # lesson_2 missing — allowed for remedial/branch
        result = check_lesson_continuity({}, tmp_path)
        assert result.passed  # Gaps are permitted; check_lesson_continuity only verifies no duplicates and starts at 1

    def test_new_naming_convention_all_present(self, tmp_path: Path):
        # New NN[.X]_描述.md convention with lesson_files in state
        (tmp_path / "02.0_I2C 协议原理.md").touch()
        (tmp_path / "02.1_I2C 协议代码_v2.md").touch()
        state = {
            "lesson_files": ["02.0_I2C 协议原理.md", "02.1_I2C 协议代码_v2.md"],
            "current_lesson": 2,
            "last_completed_lesson": 1,
        }
        result = check_lesson_continuity(state, tmp_path)
        assert result.passed

    def test_new_naming_with_variant_override(self, tmp_path: Path):
        # lesson_files says legacy name, but variant points to v2 on disk
        (tmp_path / "02.0_I2C 协议原理.md").touch()
        (tmp_path / "02.1_I2C 协议代码_v2.md").touch()  # only v2 exists
        state = {
            "lesson_files": ["02.0_I2C 协议原理.md", "02.1_I2C 协议代码.md"],
            "lesson_variants": {
                "02.1": {"active": "02.1_I2C 协议代码_v2.md"},
            },
            "current_lesson": 2,
        }
        result = check_lesson_continuity(state, tmp_path)
        assert result.passed, f"variant should satisfy base entry; got: {result.detail}"

    def test_new_naming_future_lessons_skipped(self, tmp_path: Path):
        # Only 2 of 9 planned lessons on disk — in-progress, should pass
        (tmp_path / "02.0_I2C 协议原理.md").touch()
        (tmp_path / "02.1_I2C 协议代码_v2.md").touch()
        state = {
            "lesson_files": [
                "02.0_I2C 协议原理.md",
                "02.1_I2C 协议代码_v2.md",
                "03.0_SPI 协议原理.md",
                "03.1_SPI 协议代码.md",
            ],
            "current_lesson": 2,
            "last_completed_lesson": 1,
        }
        result = check_lesson_continuity(state, tmp_path)
        assert result.passed, f"future lessons not yet generated should not fail: {result.detail}"

    def test_core_lesson_files_resolved_under_lessons_subdir(self, tmp_path: Path):
        core_dir = tmp_path / "core"
        core_dir.mkdir()
        (core_dir / "01_嵌入式硬件基础精华版.md").touch()
        state = {
            "current_mode": "core",
            "lesson_files_core": ["core/01_嵌入式硬件基础精华版.md"],
            "current_lesson": 1,
            "last_completed_lesson": 0,
        }
        result = check_lesson_continuity(state, tmp_path)
        assert result.passed, result.detail

    def test_deep_lesson_files_resolved_under_lessons_subdir(self, tmp_path: Path):
        deep_dir = tmp_path / "deep"
        deep_dir.mkdir()
        (deep_dir / "01_嵌入式硬件基础.md").touch()
        state = {
            "current_mode": "deep",
            "lesson_files_deep": ["deep/01_嵌入式硬件基础.md"],
            "current_lesson": 1,
            "last_completed_lesson": 0,
        }
        result = check_lesson_continuity(state, tmp_path)
        assert result.passed, result.detail

    def test_learn_lesson_files_resolved_under_lessons_subdir(self, tmp_path: Path):
        learn_dir = tmp_path / "learn"
        learn_dir.mkdir()
        (learn_dir / "01_gpio.learn.md").touch()
        state = {
            "current_mode": "learn",
            "lesson_files_learn": ["learn/01_gpio.learn.md"],
            "current_lesson": 1,
            "last_completed_lesson": 0,
        }
        result = check_lesson_continuity(state, tmp_path)
        assert result.passed, result.detail

    def test_practice_lesson_files_resolved_under_lessons_subdir(self, tmp_path: Path):
        practice_dir = tmp_path / "practice"
        practice_dir.mkdir()
        (practice_dir / "01_gpio.practice.md").touch()
        state = {
            "current_mode": "practice",
            "lesson_files_practice": ["practice/01_gpio.practice.md"],
            "current_lesson": 1,
            "last_completed_lesson": 0,
        }
        result = check_lesson_continuity(state, tmp_path)
        assert result.passed, result.detail


class TestCheckLessonCount:
    def test_current_matches_max(self, tmp_path: Path):
        (tmp_path / "lesson_1.md").touch()
        (tmp_path / "lesson_2.md").touch()
        state = {"current_lesson": 2}
        result = check_lesson_count(state, tmp_path)
        assert result.passed

    def test_current_is_next_to_generate(self, tmp_path: Path):
        (tmp_path / "lesson_1.md").touch()
        state = {"current_lesson": 2}
        result = check_lesson_count(state, tmp_path)
        assert result.passed  # current=2 means next to generate, max file is 1

    def test_no_lessons_dir_current_zero(self, tmp_path: Path):
        state = {"current_lesson": 0}
        result = check_lesson_count(state, tmp_path)
        assert result.passed

    def test_no_lessons_dir_current_nonzero(self, tmp_path: Path):
        state = {"current_lesson": 3}
        result = check_lesson_count(state, tmp_path)
        assert not result.passed


class TestCheckMasteryRate:
    def test_no_attempts_zero_rate(self):
        state = {"mastery_passed": 0, "mastery_failed": 0, "mastery_rate": 0.0}
        result = check_mastery_rate(state)
        assert result.passed

    def test_no_attempts_nonzero_rate(self):
        state = {"mastery_passed": 0, "mastery_failed": 0, "mastery_rate": 0.5}
        result = check_mastery_rate(state)
        assert not result.passed

    def test_correct_rate(self):
        state = {"mastery_passed": 6, "mastery_failed": 1, "mastery_rate": 0.857}
        result = check_mastery_rate(state)
        assert result.passed

    def test_incorrect_rate(self):
        state = {"mastery_passed": 5, "mastery_failed": 5, "mastery_rate": 0.3}
        result = check_mastery_rate(state)
        assert not result.passed


class TestCheckCompletedHasReport:
    def test_phase_not_completed(self, tmp_path: Path):
        state = {"phase": "learning"}
        result = check_completed_has_report(state, tmp_path)
        assert result.passed

    def test_phase_completed_with_report(self, tmp_path: Path):
        state = {"phase": "completed"}
        (tmp_path / "report.md").touch()
        result = check_completed_has_report(state, tmp_path)
        assert result.passed

    def test_phase_completed_missing_report(self, tmp_path: Path):
        state = {"phase": "completed"}
        result = check_completed_has_report(state, tmp_path)
        assert not result.passed


class TestCheckLearningHasLesson:
    def test_phase_not_learning(self, tmp_path: Path):
        (tmp_path / "lesson_1.md").touch()
        state = {"phase": "init", "current_lesson": 1}
        result = check_learning_has_lesson(state, tmp_path)
        assert result.passed

    def test_current_lesson_zero(self, tmp_path: Path):
        state = {"phase": "learning", "current_lesson": 0}
        result = check_learning_has_lesson(state, tmp_path)
        assert result.passed

    def test_lesson_file_exists(self, tmp_path: Path):
        (tmp_path / "lesson_1.md").touch()
        state = {"phase": "learning", "current_lesson": 1, "last_completed_lesson": 0}
        result = check_learning_has_lesson(state, tmp_path)
        assert result.passed

    def test_lesson_file_missing(self, tmp_path: Path):
        state = {"phase": "learning", "current_lesson": 5, "last_completed_lesson": 4}
        result = check_learning_has_lesson(state, tmp_path)
        assert not result.passed

    def test_core_current_lesson_exists(self, tmp_path: Path):
        core_dir = tmp_path / "core"
        core_dir.mkdir()
        (core_dir / "01_core.md").touch()
        state = {
            "phase": "learning",
            "current_mode": "core",
            "current_lesson": 1,
            "last_completed_lesson": 0,
            "lesson_files_core": ["core/01_core.md"],
        }
        result = check_learning_has_lesson(state, tmp_path)
        assert result.passed, result.detail

    def test_learn_current_lesson_exists(self, tmp_path: Path):
        learn_dir = tmp_path / "learn"
        learn_dir.mkdir()
        (learn_dir / "01_gpio.learn.md").touch()
        state = {
            "phase": "learning",
            "current_mode": "learn",
            "current_lesson": 1,
            "last_completed_lesson": 0,
            "lesson_files_learn": ["learn/01_gpio.learn.md"],
        }
        result = check_learning_has_lesson(state, tmp_path)
        assert result.passed, result.detail


class TestCheckLessonVariantsActive:
    def test_no_variants(self, tmp_path: Path):
        result = check_lesson_variants_active({}, tmp_path)
        assert result.passed

    def test_active_variant_exists(self, tmp_path: Path):
        (tmp_path / "02.1_I2C 协议代码_v2.md").touch()
        state = {
            "lesson_variants": {
                "02.1": {"active": "02.1_I2C 协议代码_v2.md"},
            }
        }
        result = check_lesson_variants_active(state, tmp_path)
        assert result.passed, result.detail

    def test_active_variant_missing(self, tmp_path: Path):
        state = {
            "lesson_variants": {
                "02.1": {"active": "02.1_I2C 协议代码_v2.md"},
            }
        }
        result = check_lesson_variants_active(state, tmp_path)
        assert not result.passed
        assert "02.1_I2C 协议代码_v2.md" in result.detail


# --- Diagnostic-related invariants ---

class TestDiagnosticStateInvariants:
    """诊断相关的状态不变量测试"""

    def test_background_has_diagnostic_section(self):
        """测试：background.md 包含诊断历史区域"""
        bg_path = Path("settings/background.md")
        if not bg_path.exists():
            pytest.skip("background.md not initialized")
        content = bg_path.read_text(encoding="utf-8")
        assert "诊断历史与薄弱知识点" in content

    def test_prereq_diagnostic_template_exists(self):
        """测试：诊断模板文件存在"""
        tmpl = Path(".claude/skills/learning-engine/templates/prereq-diagnostic-template.md")
        assert tmpl.exists(), f"Template not found: {tmpl}"

    def test_remediation_template_exists(self):
        """测试：补救课模板存在"""
        tmpl = Path(".claude/skills/learning-engine/templates/remediation-lesson-template.md")
        assert tmpl.exists(), f"Template not found: {tmpl}"

    def test_recheck_template_exists(self):
        """测试：复诊模板存在"""
        tmpl = Path(".claude/skills/learning-engine/templates/prereq-diagnostic-recheck-template.md")
        assert tmpl.exists(), f"Template not found: {tmpl}"

    def test_prerequisite_map_example_exists(self):
        """测试：prerequisite-map 示例文件存在"""
        example = Path("settings/prerequisite-map.example.md")
        assert example.exists(), f"Example file not found: {example}"

    def test_topic_knowledge_map_example_exists(self):
        """测试：topic-knowledge-map 示例文件存在"""
        example = Path("settings/topic-knowledge-map.example.md")
        assert example.exists(), f"Example file not found: {example}"

    def test_comprehensive_assessment_skill_exists(self):
        """测试：comprehensive-assessment skill 存在"""
        skill = Path(".claude/skills/comprehensive-assessment/SKILL.md")
        assert skill.exists(), f"Skill not found: {skill}"

    def test_knowledge_map_template_exists(self):
        """测试：知识图谱模板存在"""
        tmpl = Path(".claude/skills/comprehensive-assessment/references/knowledge-map-template.md")
        assert tmpl.exists(), f"Template not found: {tmpl}"
