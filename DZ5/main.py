import logging
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()


class Task(BaseModel):
    id: int
    title: str
    description: str
    status: str

tasks = []

@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.get("/tasks/", response_model=List[Task])
async def read_task():
    logger.info('Отработал POST запрос.')
    return tasks


@app.get("/task/{task_id}/", response_model=Task)
async def create_item(task_id: int):
    for task in tasks:
        if task:
            logger.info('Отработал POST запрос.')
            return task
    return HTTPException(status_code=404, detail="Task not found")


@app.post("/task/", response_model=Task)
async def create_task(task: Task):
    tasks.append(task)
    logger.info('Отработал POST запрос.')
    return task


@app.put("/task/{task_id}", response_model=Task)
async def update_task(task_id: int, task: Task):
    for i, task_ in enumerate(tasks):
        if task_.id == task_id:
            tasks[i] = task
            logger.info(f'Отработал PUT запрос для task id = {task_id}.')
            return task
    return HTTPException(status_code=404, detail="Task not found")


@app.delete("/task/{task_id}", response_model=Task)
async def delete_task(task_id: int):
    for i, task in enumerate(tasks):
        if task.id == task_id:
            tasks[i].status = "deleted"
            logger.info(f'Отработал PUT запрос для task id = {task_id}.')
            return task
    return HTTPException(status_code=404, detail="Task not found")