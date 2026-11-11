from __future__ import annotations

import asyncio

import pytest

from manager.command_bus_v2 import UniversalCommandBusV2
from manager.db_v3 import StoreV3
from manager.job_control_v8 import JobControlV8


def store(tmp_path):
    return StoreV3(tmp_path / "v8.sqlite")


def test_parse_job_operations():
    job = "12345678-1234-1234-1234-123456789abc"
    assert JobControlV8.parse("STATUS JOB " + job) == ("STATUS", job, "")
    assert JobControlV8.parse("CANCEL " + job) == ("CANCEL", job, "")
    assert JobControlV8.parse("CONTINUE JOB " + job + " fix colors") == (
        "CONTINUE", job, "fix colors"
    )
    assert JobControlV8.parse("APPROVE REV-123456789ABC") == (
        "APPROVE", "REV-123456789ABC", ""
    )
    assert JobControlV8.parse("please delete it") is None


def test_job_ownership_and_cancel(tmp_path):
    s = store(tmp_path)
    j = "12345678-1234-1234-1234-123456789abc"
    s.execute(
        "INSERT INTO command_jobs(id,source,source_id,request_text,status,created_at,updated_at) "
        "VALUES(?,?,?,?,?,?,?)", (j, "gmail", "m1", "status", "running", "now", "now")
    )
    v8 = JobControlV8(s)
    v8.bind(j, "owner@example.com", "t1")
    with pytest.raises(ValueError):
        v8.inspect(j, "other@example.com")
    assert v8.inspect(j, "owner@example.com")["job"]["status"] == "running"
    assert v8.cancel(j, "owner@example.com")["accepted"]
    assert v8.cancelled(j)


def test_high_impact_steps_wait_and_never_dispatch(tmp_path, monkeypatch):
    s = store(tmp_path)
    s.execute(
        "INSERT INTO mail_commands(message_id,sender,subject,target,command_text,status,received_at) "
        "VALUES(?,?,?,?,?,?,?)",
        ("m1", "owner@example.com", "[AGENT BLOGLAB]", "bloglab",
         "objavi clanek", "processing", "now"),
    )
    monkeypatch.setenv("AGENT_MANAGER_EMAIL_V8_ENABLED", "1")
    bus = UniversalCommandBusV2(s)
    async def forbid(*args, **kwargs):
        raise AssertionError("Must not execute production publication")
    monkeypatch.setattr("manager.command_bus_v2._dispatch", forbid)
    result = asyncio.run(bus.execute(
        "objavi clanek", source="gmail", source_id="m1", explicit_target="bloglab"
    ))
    assert result["status"] == "waiting_approval"
    assert result["steps"][0]["status"] == "waiting_approval"
    review = result["steps"][0]["review_id"]
    assert bus.controls.review(review, "owner@example.com", "APPROVE")["executed"] is False
    assert bus.controls.review(review, "owner@example.com", "REJECT")["status"] == "rejected"


def test_readonly_email_job_does_not_wake_model(tmp_path, monkeypatch):
    s = store(tmp_path)
    s.execute(
        "INSERT INTO mail_commands(message_id,sender,subject,target,command_text,status,received_at) "
        "VALUES(?,?,?,?,?,?,?)",
        ("m2", "owner@example.com", "[AGENT MANAGER]", "manager",
         "status", "processing", "now"),
    )
    monkeypatch.setenv("AGENT_MANAGER_EMAIL_V8_ENABLED", "1")
    bus = UniversalCommandBusV2(s)
    calls = []
    async def fake_dispatch(target, command):
        calls.append((target, command))
        return {"ok": True}
    monkeypatch.setattr("manager.command_bus_v2._dispatch", fake_dispatch)
    result = asyncio.run(bus.execute(
        "status", source="gmail", source_id="m2", explicit_target="manager"
    ))
    assert result["status"] == "completed"
    assert calls == [("manager", "status")]
    assert bus.controls.inspect(result["job_id"], "owner@example.com")["job"]["status"] == "completed"
