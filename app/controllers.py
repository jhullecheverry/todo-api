from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlmodel import Session

from app.db import get_session
from app import services

router = APIRouter()


class UserCreate(BaseModel):
    name: str
    email: str


class UserOut(BaseModel):
    id: int
    name: str
    email: str


class TaskCreate(BaseModel):
    title: str
    description: Optional[str] = None
    user_id: int


class TaskOut(BaseModel):
    id: int
    title: str
    description: Optional[str]
    is_completed: bool
    user_id: int


class TaskStatusUpdate(BaseModel):
    is_completed: bool



@router.post("/users/", response_model=UserOut)
def create_user(payload: UserCreate, session: Session = Depends(get_session)):
    user = services.create_user(session, payload.name, payload.email)
    return UserOut(id=user.id, name=user.name, email=user.email)


@router.get("/users/", response_model=List[UserOut])
def list_users(session: Session = Depends(get_session)):
    users = services.list_users(session)
    return [UserOut(id=u.id, name=u.name, email=u.email) for u in users]



@router.post("/tasks/", response_model=TaskOut)
def create_task(payload: TaskCreate, session: Session = Depends(get_session)):
    user = services.get_user(session, payload.user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    task = services.create_task(session, payload.title, payload.description or "", payload.user_id)
    return TaskOut(
        id=task.id,
        title=task.title,
        description=task.description,
        is_completed=task.is_completed,
        user_id=task.user_id,
    )


@router.get("/tasks/user/{user_id}", response_model=List[TaskOut])
def list_tasks_by_user(user_id: int, session: Session = Depends(get_session)):
    user = services.get_user(session, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    tasks = services.list_tasks_by_user(session, user_id)
    return [
        TaskOut(
            id=t.id,
            title=t.title,
            description=t.description,
            is_completed=t.is_completed,
            user_id=t.user_id,
        )
        for t in tasks
    ]


@router.put("/tasks/{task_id}/status", response_model=TaskOut)
def update_task_status(task_id: int, payload: TaskStatusUpdate, session: Session = Depends(get_session)):
    task = services.update_task_status(session, task_id, payload.is_completed)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return TaskOut(
        id=task.id,
        title=task.title,
        description=task.description,
        is_completed=task.is_completed,
        user_id=task.user_id,
    )


@router.delete("/tasks/{task_id}", response_model=dict)
def delete_task(task_id: int, session: Session = Depends(get_session)):
    ok = services.delete_task(session, task_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Task not found")
    return {"deleted": True}
