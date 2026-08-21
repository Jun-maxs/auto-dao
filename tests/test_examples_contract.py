"""Repository examples should document both legacy and current session shapes."""

from __future__ import annotations

import json
import re
from pathlib import Path

from scripts.ci.check_examples import check_session


PROJECT_ROOT = Path(__file__).resolve().parents[1]
EXAMPLES_ROOT = PROJECT_ROOT / "examples" / "learning-history"
RECOMMENDED_EXAMPLE = EXAMPLES_ROOT / "new-version-stm32-spi-mini_2026-04-18"


def test_check_examples_accepts_structured_lessons(tmp_path: Path):
    session = tmp_path / "new-version-session"
    (session / "lessons" / "learn").mkdir(parents=True)
    (session / "summary.md").write_text("# Summary\n", encoding="utf-8")
    (session / "roadmap_status.md").write_text("# Roadmap\n", encoding="utf-8")
    (session / "lessons" / "learn" / "01_demo.learn.md").write_text(
        "# Learn card\n",
        encoding="utf-8",
    )

    assert check_session(session) == []


def test_recommended_new_version_example_is_sanitized_and_documented():
    assert RECOMMENDED_EXAMPLE.is_dir()
    assert (RECOMMENDED_EXAMPLE / "session_state.json").is_file()
    assert (RECOMMENDED_EXAMPLE / "lessons" / "learn" / "03_SPI协议原理.learn.md").is_file()

    readme = (EXAMPLES_ROOT / "README.md").read_text(encoding="utf-8")
    assert "new-version-stm32-spi-mini_2026-04-18" in readme
    assert "新版主推荐" in readme

    combined_text = "\n".join(
        file.read_text(encoding="utf-8")
        for file in RECOMMENDED_EXAMPLE.rglob("*")
        if file.is_file() and file.suffix.lower() in {".md", ".json"}
    )
    assert not re.search(r"\b[A-Za-z]:[\\/]", combined_text)
    assert "PDF" in combined_text
    assert "图片" in combined_text
    assert "私有路径" in combined_text
    assert "大目录" in combined_text

    state = json.loads((RECOMMENDED_EXAMPLE / "session_state.json").read_text(encoding="utf-8"))
    assert state["schema_version"] == "2.3"
    assert state["source_path"].startswith("examples/sources/")
