import os
import subprocess
import sys
import tempfile
import time

import httpx
import pytest

UVICORN_CMD = [sys.executable, "-m", "uvicorn", "main:app", "--port", "8001", "--host", "127.0.0.1", "--log-level", "warning"]


@pytest.fixture(scope="module")
def server():
    env = os.environ.copy()
    tmp = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
    env["DATABASE_URL"] = f"sqlite:///{tmp.name}"
    proc = subprocess.Popen(UVICORN_CMD, env=env)
    # wait for server to be ready (basic)
    time.sleep(1.0)
    yield
    proc.terminate()
    try:
        proc.wait(timeout=5)
    except Exception:
        proc.kill()


def test_e2e_flow(server):
    base = "http://127.0.0.1:8001"
    with httpx.Client(base_url=base, timeout=5) as client:
        # create user
        r = client.post("/users/", json={"name": "E2E User", "email": "e2e@example.com"})
        assert r.status_code == 200
        user_id = r.json()["id"]

        # create task
        r = client.post("/tasks/", json={"title": "E2E Task", "description": "desc", "user_id": user_id})
        assert r.status_code == 200
        task_id = r.json()["id"]

        # list
        r = client.get(f"/tasks/user/{user_id}")
        assert r.status_code == 200
        assert any(t["id"] == task_id for t in r.json())

        # update
        r = client.put(f"/tasks/{task_id}/status", json={"is_completed": True})
        assert r.status_code == 200
        assert r.json()["is_completed"] is True

        # delete
        r = client.delete(f"/tasks/{task_id}")
        assert r.status_code == 200
        assert r.json()["deleted"] is True