from sqlalchemy.orm import Session
from . import models, schemas

class TodoRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_todo(self, todo_id: int):
        return self.db.query(models.Todo).filter(models.Todo.id == todo_id).first()

    def get_todos_by_user(self, user_id: int, skip: int = 0, limit: int = 100):
        return self.db.query(models.Todo).filter(models.Todo.user_id == user_id).offset(skip).limit(limit).all()

    def create_todo(self, todo: schemas.TodoCreate, user_id: int):
        db_todo = models.Todo(**todo.model_dump(), user_id=user_id)
        self.db.add(db_todo)
        self.db.commit()
        self.db.refresh(db_todo)
        return db_todo

    def update_todo(self, todo_id: int, todo_update: schemas.TodoUpdate):
        db_todo = self.get_todo(todo_id)
        if db_todo:
            for field, value in todo_update.model_dump(exclude_unset=True).items():
                setattr(db_todo, field, value)
            self.db.commit()
            self.db.refresh(db_todo)
        return db_todo

    def delete_todo(self, todo_id:int):
        db_todo = self.get_todo(todo_id)
        if db_todo:
            self.db.delete(db_todo)
            self.db.commit()
            return True
        return False
