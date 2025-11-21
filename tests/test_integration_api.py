import importlib
import os

import pytest
from fastapi.testclient import TestClient


@pytest.fixture(autouse=True)
def setup_db(tmp_path, monkeypatch):
    db_file = tmp_path / "test_integration.db"
    monkeypatch.setenv("DATABASE_URL", f"sqlite:///{db_file}")

    import app.db as dbmod  
    importlib.reload(dbmod)

    import app.controllers as controllers
    importlib.reload(controllers)
    import main as mainmod 
    importlib.reload(mainmod)
    yield


def test_api_flow():
    from main import app  
    client = TestClient(app)


    r = client.post("/users/", json={"name": "Dora", "email": "dora@example.com"})
    assert r.status_code == 200
    user = r.json()
    user_id = user["id"]


    r = client.post("/tasks/", json={"title": "Do stuff", "description": "Important", "user_id": user_id})
    assert r.status_code == 200
    task = r.json()
    task_id = task["id"]

 
    r = client.get(f"/tasks/user/{user_id}")
    assert r.status_code == 200
    tasks = r.json()
    assert any(t["id"] == task_id for t in tasks)


    r = client.put(f"/tasks/{task_id}/status", json={"is_completed": True})
    assert r.status_code == 200
    assert r.json()["is_completed"] is True


    r = client.delete(f"/tasks/{task_id}")
    assert r.status_code == 200
    assert r.json()["deleted"] is True
