from .repository import TodoRepository
from . import schemas

class TodoService:
    def __init__(self, repository: TodoRepository):
        self.repository = repository

    def get_todo(self, todo_id: int):
        return self.repository.get_todo(todo_id)

    def get_todos_by_user(self, user_id: int, skip: int = 0, limit: int = 100):
        return self.repository.get_todos_by_user(user_id, skip, limit)

    def create_todo(self, todo: schemas.TodoCreate, user_id: int):
        return self.repository.create_todo(todo, user_id)

    def update_todo(self, todo_id: int, todo_update: schemas.TodoUpdate):
        return self.repository.update_todo(todo_id, todo_update)
        
    def delete_todo(self, todo_id: int):
        return self.repository.delete_todo(todo_id)
