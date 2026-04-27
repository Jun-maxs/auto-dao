"""Tests for scripts/session/reconcile_state.py."""

from __future__ import annotations

import json
from pathlib import Path

from scripts.session.reconcile_state import reconcile_session


def _write_session(tmp_path: Path, state: dict) -> Path:
    session = tmp_path / "session"
    (session / "lessons").mkdir(parents=True)
    (session / "session_state.json").write_text(
        json.dumps(state, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    return session


def _read_state(session: Path) -> dict:
    return json.loads((session / "session_state.json").read_text(encoding="utf-8"))


def test_reconcile_is_read_only_by_default(tmp_path: Path):
    session = _write_session(
        tmp_path,
        {
            "wait_reason": "waiting_for_user_answer_L01",
            "current_mode": "core",
        },
    )

    changed, findings, backup = reconcile_session(session)

    assert not changed
    assert backup is None
    assert any(finding.kind == "wait_reason" for finding in findings)
    assert _read_state(session)["wait_reason"] == "waiting_for_user_answer_L01"


def test_fix_wait_reason_moves_detail_and_writes_backup(tmp_path: Path):
    session = _write_session(
        tmp_path,
        {
            "wait_reason": "waiting_for_user_answer_L01",
            "current_mode": "core",
        },
    )

    changed, findings, backup = reconcile_session(session, fix_wait_reason=True)
    state = _read_state(session)

    assert changed
    assert backup is not None and backup.exists()
    assert state["wait_reason"] == "awaiting_answer"
    assert state["wait_detail"]["message"] == "waiting_for_user_answer_L01"
    assert state["wait_detail"]["lesson_id"] == "01"
    assert any(finding.fixed for finding in findings)


def test_fix_missing_active_variant_uses_existing_candidate(tmp_path: Path):
    session = _write_session(
        tmp_path,
        {
            "wait_reason": None,
            "lesson_variants": {
                "02.1": {"active": "02.1_I2C 协议代码_v2.md"},
            },
        },
    )
    (session / "lessons" / "02.1_I2C 协议代码.md").write_text("# legacy", encoding="utf-8")

    changed, findings, backup = reconcile_session(session, fix_lesson_files=True)
    state = _read_state(session)

    assert changed
    assert backup is not None and backup.exists()
    assert state["lesson_variants"]["02.1"]["active"] == "02.1_I2C 协议代码.md"
    assert any(finding.kind == "lesson_variant_active" for finding in findings)


def test_fix_active_core_file_list_uses_scoped_candidate(tmp_path: Path):
    session = _write_session(
        tmp_path,
        {
            "wait_reason": None,
            "current_mode": "core",
            "current_lesson": 1,
            "last_completed_lesson": 0,
            "lesson_files_core": ["core/03_SPI 精华版_v2.md"],
        },
    )
    (session / "lessons" / "core").mkdir()
    (session / "lessons" / "core" / "03_SPI 精华版.md").write_text("# core", encoding="utf-8")

    changed, findings, backup = reconcile_session(session, fix_lesson_files=True)
    state = _read_state(session)

    assert changed
    assert backup is not None and backup.exists()
    assert state["lesson_files_core"] == ["core/03_SPI 精华版.md"]
    assert any(finding.kind == "lesson_file_missing" for finding in findings)


def test_fix_active_core_file_list_does_not_cross_mode_scope(tmp_path: Path):
    session = _write_session(
        tmp_path,
        {
            "wait_reason": None,
            "current_mode": "core",
            "current_lesson": 1,
            "last_completed_lesson": 0,
            "lesson_files_core": ["core/03_SPI 精华版.md"],
        },
    )
    (session / "lessons" / "03.0_SPI 协议原理.md").write_text("# deep legacy", encoding="utf-8")

    changed, findings, backup = reconcile_session(session, fix_lesson_files=True)
    state = _read_state(session)

    assert not changed
    assert backup is None
    assert state["lesson_files_core"] == ["core/03_SPI 精华版.md"]
    assert any(finding.suggestion == "no candidate found" for finding in findings)


def test_write_audit_records_repair_log(tmp_path: Path):
    session = _write_session(
        tmp_path,
        {
            "wait_reason": "waiting_for_user_answer_L01",
            "current_mode": "core",
        },
    )

    changed, _, _ = reconcile_session(session, fix_wait_reason=True, write_audit=True)
    state = _read_state(session)

    assert changed
    assert state["state_repair_log"]
    assert state["state_repair_log"][0]["fix_wait_reason"] is True
