import pytest
from sqlmodel import create_engine, Session, SQLModel

from app.services import create_user, get_user, list_users, create_task, list_tasks_by_user, update_task_status, delete_task


@pytest.fixture
def session():
    engine = create_engine("sqlite:///:memory:")
    SQLModel.metadata.create_all(engine)
    with Session(engine) as s:
        yield s


def test_user_service_create_and_get(session):
    user = create_user(session, "Alice", "alice@example.com")
    assert user.id is not None
    fetched = get_user(session, user.id)
    assert fetched is not None
    assert fetched.email == "alice@example.com"


def test_list_users(session):
    create_user(session, "Bob", "bob@example.com")
    users = list_users(session)
    assert len(users) == 1


def test_task_services_crud(session):
    user = create_user(session, "Charlie", "charlie@example.com")
    task = create_task(session, "Task 1", "desc", user.id)
    assert task.id is not None

    tasks = list_tasks_by_user(session, user.id)
    assert len(tasks) == 1

    updated = update_task_status(session, task.id, True)
    assert updated is not None
    assert updated.is_completed is True

    deleted = delete_task(session, task.id)
    assert deleted is True

    tasks_after = list_tasks_by_user(session, user.id)
    assert len(tasks_after) == 0