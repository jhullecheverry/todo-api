from typing import List, Optional

from sqlmodel import Session, select

from app.models import Task, User


# User services
def create_user(session: Session, name: str, email: str) -> User:
    user = User(name=name, email=email)
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


def get_user(session: Session, user_id: int) -> Optional[User]:
    return session.get(User, user_id)


def list_users(session: Session) -> List[User]:
    return session.exec(select(User)).all()



def create_task(session: Session, title: str, description: str, user_id: int) -> Task:
    task = Task(title=title, description=description, user_id=user_id)
    session.add(task)
    session.commit()
    session.refresh(task)
    return task


def list_tasks_by_user(session: Session, user_id: int) -> List[Task]:
    statement = select(Task).where(Task.user_id == user_id)
    return session.exec(statement).all()


def update_task_status(session: Session, task_id: int, is_completed: bool) -> Optional[Task]:
    task = session.get(Task, task_id)
    if not task:
        return None
    task.is_completed = is_completed
    session.add(task)
    session.commit()
    session.refresh(task)
    return task


def delete_task(session: Session, task_id: int) -> bool:
    task = session.get(Task, task_id)
    if not task:
        return False
    session.delete(task)
    session.commit()
    return True

