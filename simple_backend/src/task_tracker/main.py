
import json, os
from fastapi import FastAPI
from pydantic import BaseModel


app = FastAPI() # Создаем приложение FastAPI — это как веб-сервер, который отвечает на запросы


class Task(BaseModel):  # Описание модели задачи. Task — полная задача, TaskCreate — только с названием (для создания новой задачи)
    id: int # Уникальный номер задачи
    title: str  # Название задачи
    status: bool = False  # Выполнена задача или нет (по умолчанию — нет)

class TaskCreate(BaseModel):
    title: str  # Только название задачи (без ID и статуса)


class TaskStorage:  # Класс TaskStorage управляет хранением задач в файле
    def __init__(self, filename):
        self.filename = filename  # Название файла, где хранятся задачи

    def load_tasks(self):
        if os.path.exists(self.filename):    # Загружаем задачи из файла, если файл существует
            with open(self.filename, 'r', encoding='utf-8') as file:
                return [Task(**task) for task in json.load(file)]  # Преобразуем данные из файла в объекты Task
        return []  # Если файла нет, возвращаем пустой список

    def save_tasks(self,tasks):
        with open(self.filename, 'w', encoding='utf-8') as file:    # Сохраняем список задач в файл
            json.dump([task.dict() for task in tasks], file, ensure_ascii=False, indent=4)  # Сохраняем в JSON

storage = TaskStorage('tasks.json') # Создаем объект для управления задачами, указываем имя файла

@app.get("/tasks")  # Получаем все задачи
def get_tasks():
    return storage.load_tasks()  # Возвращаем список всех задач

@app.post("/tasks") # Создаем новую задачу
def create_task(task_data: TaskCreate):
    tasks = storage.load_tasks()  # Загружаем текущие задачи
    task_id = len(tasks) + 1 if not tasks else max(task.id for task in tasks) + 1    # Генерируем ID: если задач нет, то 1, иначе находим максимальный ID и прибавляем 1
    new_task = Task(id=task_id, title=task_data.title, status=False)      # Создаем новую задачу с уникальным ID и статусом False
    tasks.append(new_task)  # Добавляем новую задачу в список
    storage.save_tasks(tasks)  # Сохраняем список обратно в файл
    return new_task  # Возвращаем созданную задачу

@app.put("/tasks/{task_id}")    # Обновляем существующую задачу по ID
def update_task(task_id: int, task_data: TaskCreate):
    tasks = storage.load_tasks()  # Загружаем текущие задачи
    for task in tasks:
        if task.id == task_id:  # Если нашли задачу с нужным ID
            task.title = task_data.title  # Меняем её название
            storage.save_tasks(tasks)  # Сохраняем изменения
            return task  # Возвращаем обновлённую задачу
    return {'error': 'Task not found'}  # Если не нашли — возвращаем сообщение об ошибке

@app.delete("/tasks/{task_id}")    # Удаляем задачу по ID
def delete_task(task_id: int):
    tasks = storage.load_tasks()  # Загружаем текущие задачи
    new_tasks = [task for task in tasks if task.id != task_id]  # Убираем задачу с нужным ID
    if len(new_tasks) == len(tasks):
        return {"message":"Task deleted"}  # Если ничего не удалили, значит задача не найдена
    storage.save_tasks(new_tasks)  # Сохраняем обновлённый список задач
    return {"message": "Task deleted"}  # Возвращаем сообщение об успешном удалении




