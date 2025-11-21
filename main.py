import uvicorn
from fastapi import FastAPI

from app.controllers import router as api_router
from app.db import create_db_and_tables

app = FastAPI(title="ToDo API - layered example")

app.include_router(api_router)


@app.on_event("startup")
def on_startup():
    create_db_and_tables()


if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)