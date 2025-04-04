
import json
import os
import requests
from fastapi import FastAPI
from pydantic import BaseModel


app = FastAPI() # Создаем приложение FastAPI — это как веб-сервер, который отвечает на запросы

class Task(BaseModel):  # Описание модели задачи. Task — полная задача, TaskCreate — только с названием (для создания новой задачи)
    id: int # Уникальный номер задачи
    title: str  # Название задачи
    status: bool = False  # Выполнена задача или нет (по умолчанию — False)

class TaskCreate(BaseModel):
    title: str  # Только название задачи (без ID и статуса)

class CloudFlareAPI:    # Класс для работы с Cloudflare Workers AI (интеграция через REST API)
    def __init__(self, api_url: str, api_key: str):
        self.api_url = api_url  # URL-адрес Cloudflare API
        self.api_key = api_key  # Ключ доступа к Cloudflare API

    def post_data(self, data:dict):
        headers = {     # Отправка POST-запроса с JSON-данными в Cloudflare
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        }
        response = requests.post(self.api_url, headers=headers, json=data)
        return response.json()      # Возвращаем ответ в формате JSON

    def run(self, model: str, inputs: list):    # Метод для выполнения задачи через Cloudflare AI
        headers = {     # Заголовки запроса
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        }
        input_data = {"messages": inputs}    # Формируем данные для отправки
        response = requests.post(f"{self.api_url}{model}", headers=headers, json=input_data)    # Отправляем запрос на выполнение модели
        return response.json()    # Возвращаем ответ

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
    cloudflare_api = CloudFlareAPI(  # Создаем объект для работы с Cloudflare API
        api_url="https://api.cloudflare.com/client/v4/accounts/e959035eda5785e18c0c699884ac8b13/ai/run/",
        api_key="0vP-4yVrIoQjNe4qvjKwHfNVlZRCdjuOmnpm_Ovz"
    )
    inputs = [   # Формируем запрос для AI, чтобы объяснить, как выполнить задачу
        {"role": "system", "content": "You are a helpful assistant that explains how to solve tasks."},
        {"role": "user", "content": f"Explain how to solve the task: {task_data.title}"}
    ]
    llm_response = cloudflare_api.run("@cf/meta/llama-3-8b-instruct", inputs)   # Отправляем запрос в Cloudflare AI

    return {     # Возвращаем созданную задачу и ответ от AI
        "task": new_task,
        "llm_response": llm_response
    }

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

