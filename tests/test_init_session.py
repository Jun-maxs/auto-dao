"""Tests for scripts/session/init_session.py.

Verifies that the one-shot session initialiser produces a directory that
passes ``validate_state.py`` out of the box and that all derived-view
filenames match SKILL.md + _file_paths conventions.
"""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from scripts.session.init_session import init_session
from scripts.session.validate_state import validate


# ---------------------------------------------------------------------------
# Happy path
# ---------------------------------------------------------------------------


def _make_source(tmp_path: Path, name: str = "source.md") -> Path:
    p = tmp_path / name
    p.write_text("# Source material\n\nsome content\n", encoding="utf-8")
    return p


class TestInitSessionHappyPath:
    """成功路径：所有派生视图文件、JSON 字段、hash 计算都应就绪。"""

    def test_creates_directory_tree(self, tmp_path: Path):
        src = _make_source(tmp_path)
        session = init_session(
            topic_id="demo-topic",
            source_path=str(src),
            base_dir=tmp_path / "learning-history",
            timestamp="2026-04-18-08-00",
            learning_language="zh",
            total_lessons=3,
        )
        assert session.is_dir()
        assert session.name == "demo-topic_2026-04-18-08-00"
        assert (session / "lessons").is_dir()
        assert (session / "lessons" / "learn").is_dir()
        assert (session / "lessons" / "practice").is_dir()
        assert (session / "lessons" / "deep").is_dir()
        assert (session / "source_coverage").is_dir()

    def test_all_derived_views_present(self, tmp_path: Path):
        src = _make_source(tmp_path)
        session = init_session(
            topic_id="demo-topic",
            source_path=str(src),
            base_dir=tmp_path / "learning-history",
            timestamp="2026-04-18-08-00",
        )
        # Bare filenames (unified with SKILL.md prose + examples/)
        for name in [
            "summary.md",
            "roadmap_status.md",
            "_ai_context.md",
            "course_overview.md",
            "session_state.json",
            "metrics.json",
            "review_queue.json",
        ]:
            assert (session / name).exists(), f"missing {name}"

    def test_session_state_schema_fields(self, tmp_path: Path):
        src = _make_source(tmp_path)
        session = init_session(
            topic_id="demo-topic",
            source_path=str(src),
            topic_name="Demo Topic 演示",
            base_dir=tmp_path / "learning-history",
            timestamp="2026-04-18-08-00",
            learning_language="zh",
            total_lessons=3,
        )
        state = json.loads((session / "session_state.json").read_text(encoding="utf-8"))
        assert state["schema_version"] == "2.3"
        assert state["topic_id"] == "demo-topic"
        assert state["topic_name"] == "Demo Topic 演示"
        assert state["source_path"] == str(src)
        assert state["processed_path"] == str(src)
        assert state["phase"] == "learning"
        assert state["total_lessons"] == 3
        assert state["learning_language"] == "zh"
        assert state["current_mode"] == "learn"
        assert state["lesson_files_learn"] == []
        assert state["lesson_files_practice"] == []
        assert state["lesson_files_core"] == []
        assert state["lesson_files_deep"] == []
        assert state["mode_switch_log"] == []
        assert state["_file_paths"]["source_coverage"] == "source_coverage/"
        assert state["source_hash"].startswith("sha256:")
        assert state["created_at"] and state["updated_at"]
        # learner_model defaults
        lm = state["learner_model"]
        assert lm["bloom_target"] == 3
        assert lm["overall_confidence_bias"] == "unknown"
        assert lm["concept_mastery"] == {}
        assert lm["last_updated_at"]
        # _file_paths uses bare filenames
        fp = state["_file_paths"]
        assert fp["summary"] == "summary.md"
        assert fp["session_state"] == "session_state.json"

    def test_metrics_has_unique_session_id(self, tmp_path: Path):
        src = _make_source(tmp_path)
        s1 = init_session(
            topic_id="demo1",
            source_path=str(src),
            base_dir=tmp_path / "learning-history",
            timestamp="2026-04-18-08-00",
        )
        s2 = init_session(
            topic_id="demo2",
            source_path=str(src),
            base_dir=tmp_path / "learning-history",
            timestamp="2026-04-18-08-00",
        )
        m1 = json.loads((s1 / "metrics.json").read_text(encoding="utf-8"))
        m2 = json.loads((s2 / "metrics.json").read_text(encoding="utf-8"))
        assert m1["session_id"] and m2["session_id"]
        assert m1["session_id"] != m2["session_id"]
        assert m1["events"] == []

    def test_output_passes_validate_state(self, tmp_path: Path):
        """init_session 的产物必须立刻通过 validate_state.py 的所有检查。"""
        src = _make_source(tmp_path)
        session = init_session(
            topic_id="demo-topic",
            source_path=str(src),
            base_dir=tmp_path / "learning-history",
            timestamp="2026-04-18-08-00",
            total_lessons=3,
        )
        # current_lesson defaults to 0 → phase='learning' & current_lesson=0 should pass
        results = validate(session)
        failed = [r for r in results if not r.passed]
        # Debug aid on failure
        assert not failed, "validate_state failures:\n" + "\n".join(str(r) for r in failed)


# ---------------------------------------------------------------------------
# Error paths
# ---------------------------------------------------------------------------


class TestInitSessionErrors:
    def test_missing_topic_id(self, tmp_path: Path):
        with pytest.raises(ValueError):
            init_session(topic_id="", source_path="foo.md", base_dir=tmp_path)

    def test_missing_source_path(self, tmp_path: Path):
        with pytest.raises(ValueError):
            init_session(topic_id="x", source_path="", base_dir=tmp_path)

    def test_existing_directory_without_force(self, tmp_path: Path):
        src = _make_source(tmp_path)
        init_session(
            topic_id="demo",
            source_path=str(src),
            base_dir=tmp_path / "h",
            timestamp="2026-04-18-08-00",
        )
        with pytest.raises(FileExistsError):
            init_session(
                topic_id="demo",
                source_path=str(src),
                base_dir=tmp_path / "h",
                timestamp="2026-04-18-08-00",
            )

    def test_existing_directory_with_force(self, tmp_path: Path):
        src = _make_source(tmp_path)
        session = init_session(
            topic_id="demo",
            source_path=str(src),
            base_dir=tmp_path / "h",
            timestamp="2026-04-18-08-00",
        )
        # Write a marker file into lessons/
        (session / "lessons" / "lesson_1.md").write_text("old", encoding="utf-8")
        assert (session / "lessons" / "lesson_1.md").exists()

        # Re-init with force should wipe the directory
        init_session(
            topic_id="demo",
            source_path=str(src),
            base_dir=tmp_path / "h",
            timestamp="2026-04-18-08-00",
            force=True,
        )
        assert not (session / "lessons" / "lesson_1.md").exists()


# ---------------------------------------------------------------------------
# Source hash
# ---------------------------------------------------------------------------


class TestSourceHash:
    def test_hash_empty_when_source_missing(self, tmp_path: Path):
        session = init_session(
            topic_id="demo",
            source_path=str(tmp_path / "nonexistent.md"),
            base_dir=tmp_path / "h",
            timestamp="2026-04-18-08-00",
        )
        state = json.loads((session / "session_state.json").read_text(encoding="utf-8"))
        assert state["source_hash"] == ""

    def test_hash_matches_sha256(self, tmp_path: Path):
        import hashlib
        src = tmp_path / "data.md"
        content = b"deterministic content for hashing test\n"
        src.write_bytes(content)
        expected = "sha256:" + hashlib.sha256(content).hexdigest()

        session = init_session(
            topic_id="demo",
            source_path=str(src),
            base_dir=tmp_path / "h",
            timestamp="2026-04-18-08-00",
        )
        state = json.loads((session / "session_state.json").read_text(encoding="utf-8"))
        assert state["source_hash"] == expected
