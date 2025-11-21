import importlib
import os

import pytest
from fastapi.testclient import TestClient

# Ensure the test sets DATABASE_URL before app/db is imported
@pytest.fixture(autouse=True)
def setup_db(tmp_path, monkeypatch):
    db_file = tmp_path / "test_integration.db"
    monkeypatch.setenv("DATABASE_URL", f"sqlite:///{db_file}")
    # reload modules that read DATABASE_URL at import
    import app.db as dbmod  # noqa: E402
    importlib.reload(dbmod)
    # reload controllers/main which may have cached the engine
    import app.controllers as controllers  # noqa: E402
    importlib.reload(controllers)
    import main as mainmod  # noqa: E402
    importlib.reload(mainmod)
    yield


def test_api_flow():
    from main import app  # import after monkeypatch/reload
    client = TestClient(app)

    # create user
    r = client.post("/users/", json={"name": "Dora", "email": "dora@example.com"})
    assert r.status_code == 200
    user = r.json()
    user_id = user["id"]

    # create task
    r = client.post("/tasks/", json={"title": "Do stuff", "description": "Important", "user_id": user_id})
    assert r.status_code == 200
    task = r.json()
    task_id = task["id"]

    # list tasks for user
    r = client.get(f"/tasks/user/{user_id}")
    assert r.status_code == 200
    tasks = r.json()
    assert any(t["id"] == task_id for t in tasks)

    # update status
    r = client.put(f"/tasks/{task_id}/status", json={"is_completed": True})
    assert r.status_code == 200
    assert r.json()["is_completed"] is True

    # delete
    r = client.delete(f"/tasks/{task_id}")
    assert r.status_code == 200
    assert r.json()["deleted"] is True