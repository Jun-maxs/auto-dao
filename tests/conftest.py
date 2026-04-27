"""Shared pytest fixtures and configuration for auto-tutor tests."""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

# Ensure project root is on sys.path for all test modules
PROJECT_ROOT = Path(__file__).parent.parent
SCRIPTS_DIR = PROJECT_ROOT / "scripts"

# Ensure both project root and scripts/ are on sys.path for all test modules
for path in [str(SCRIPTS_DIR), str(PROJECT_ROOT)]:
    if path not in sys.path:
        sys.path.insert(0, path)


# ---------------------------------------------------------------------------
# Fixtures: Session / Project
# ---------------------------------------------------------------------------

@pytest.fixture(scope="session")
def project_root() -> Path:
    """Path to the project root directory."""
    return PROJECT_ROOT


@pytest.fixture(scope="session")
def session_schema(project_root: Path) -> dict:
    """Load session-state.schema.json once per session."""
    schema_path = (
        project_root
        / ".claude"
        / "skills"
        / "learning-engine"
        / "templates"
        / "session-state.schema.json"
    )
    return json.loads(schema_path.read_text(encoding="utf-8"))


# ---------------------------------------------------------------------------
# Fixtures: Temp Material Folders (for indexer tests)
# ---------------------------------------------------------------------------

@pytest.fixture
def temp_material_folder(tmp_path: Path) -> Path:
    """Create a minimal valid material folder structure.

    Creates:
        tmp_path/material_001/
            full.md           (with heading + body text)
            images/            (empty directory)
    """
    folder = tmp_path / "material_001"
    folder.mkdir()
    (folder / "full.md").write_text(
        "# 测试章节标题\n\n这是正文内容，包含关键概念。\n\n## 第二级标题\n\n更多内容。\n",
        encoding="utf-8",
    )
    images = folder / "images"
    images.mkdir()
    return folder


@pytest.fixture
def temp_material_with_images(tmp_path: Path) -> Path:
    """Create a material folder with a full.md that references an image."""
    folder = tmp_path / "material_002"
    folder.mkdir()
    (folder / "full.md").write_text(
        "# SPI 协议\n\n![图片说明](images/abc123def456.jpg)\n\n"
        "SPI 是串行外设接口。\n\n## CPOL\n\n时钟极性。\n",
        encoding="utf-8",
    )
    images = folder / "images"
    images.mkdir()
    # Create a dummy image file
    (images / "abc123def456.jpg").write_bytes(b"\xff\xd8\xff\xe0 dummy image")
    return folder


@pytest.fixture
def temp_multiple_materials(tmp_path: Path) -> list[Path]:
    """Create two material folders for cross-material testing."""
    folder_a = tmp_path / "material_A_001"
    folder_b = tmp_path / "material_B_002"
    for folder in (folder_a, folder_b):
        folder.mkdir()
        (folder / "full.md").write_text(
            "# SPI 协议\n\n## 时钟信号\n\n正文内容。\n",
            encoding="utf-8",
        )
        (folder / "images").mkdir()
    return [folder_a, folder_b]


# ---------------------------------------------------------------------------
# Fixtures: Temp Learning Session (for validate_state tests)
# ---------------------------------------------------------------------------

@pytest.fixture
def temp_session(tmp_path: Path) -> Path:
    """Create a minimal valid session directory structure."""
    session = tmp_path / "test-session_2026-04-15-10-00"
    session.mkdir()
    lessons = session / "lessons"
    lessons.mkdir()

    # Valid session_state.json (schema v2.3)
    state = {
        "schema_version": "2.3",
        "topic_id": "test-topic",
        "source_path": "test.pdf",
        "phase": "learning",
        "current_lesson": 1,
        "total_lessons": 5,
        "created_at": "2026-01-01T00:00:00+08:00",
        "updated_at": "2026-01-01T00:00:00+08:00",
        "counterfactual_mode": "off",
        "wait_reason": "awaiting_answer",
        "mastery_passed": 0,
        "mastery_failed": 0,
        "mastery_rate": 0.0,
    }
    (session / "session_state.json").write_text(
        json.dumps(state, ensure_ascii=False), encoding="utf-8"
    )
    return session


# ---------------------------------------------------------------------------
# Fixtures: Temp Review Queue
# ---------------------------------------------------------------------------

@pytest.fixture
def temp_review_queue(tmp_path: Path) -> Path:
    """Create a session dir with review_queue.json."""
    session = tmp_path / "review-session"
    session.mkdir()
    queue_file = session / "review_queue.json"
    queue_data = {
        "schema_version": "1.0",
        "items": [
            {
                "lesson": 1,
                "question_index": 0,
                "status": "pending",
                "next_review_at": "2020-01-01T00:00:00+00:00",
                "topic_tag": "SPI CPOL",
                "first_wrong_at": "2026-04-01",
                "review_count": 0,
            },
            {
                "lesson": 1,
                "question_index": 2,
                "status": "reviewed",
                "next_review_at": "2099-01-01T00:00:00+00:00",
                "topic_tag": "时钟信号",
                "first_wrong_at": "2026-04-01",
                "review_count": 1,
            },
        ]
    }
    queue_file.write_text(json.dumps(queue_data, ensure_ascii=False), encoding="utf-8")
    return session
