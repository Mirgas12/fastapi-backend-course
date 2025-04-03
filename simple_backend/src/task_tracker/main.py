'''from fastapi import FastAPI

app = FastAPI()

@app.get("/tasks")
def get_tasks():
    pass

@app.post("/tasks")
def create_task(task):
    pass

@app.put("/tasks/{task_id}")
def update_task(task_id: int):
    pass

@app.delete("/tasks/{task_id}")
def delete_task(task_id: int):
    pass
'''

import json, os
from fastapi import FastAPI
from pydantic import BaseModel


app = FastAPI()

tasks = 'tasks.json'

class Task(BaseModel):
    id: int
    title: str
    status: bool = False

class TaskCreate(BaseModel):
    title: str

def load_tasks():
    if os.path.exists(tasks):
        with open(tasks, 'r', encoding='utf-8') as file:
            return [Task(**task) for task in json.load(file)]
    return []

def save_tasks(tasks1):
    with open(tasks, 'w', encoding='utf-8') as file:
        json.dump([task.dict() for task in tasks1], file, ensure_ascii=False, indent=4)


@app.get("/tasks")
def get_tasks():
    tasks = load_tasks()
    return tasks


@app.post("/tasks")
def create_task(task_data: TaskCreate):
    tasks = load_tasks()
    task_id = len(tasks) + 1 if not tasks else max(task.id for task in tasks) + 1
    new_task = Task(id=task_id, title=task_data.title, status=False)
    tasks.append(new_task)
    save_tasks(tasks)
    return new_task

@app.put("/tasks/{task_id}")
def update_task(task_id: int, task_data: TaskCreate):
    tasks = load_tasks()
    for task1 in tasks:
        if task1.id == task_id:
            task1.title = task_data.title
            save_tasks(tasks)
            return task1
    return {'error': 'Task not found'}



@app.delete("/tasks/{task_id}")
def delete_task(task_id: int):
    tasks = load_tasks()
    new_tasks = [task for task in tasks if task.id != task_id]
    if len(new_tasks) == len(tasks):
        return {"message":"Task deleted"}
    save_tasks(new_tasks)
    return {"message": "Task deleted"}



