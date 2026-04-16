from fastapi import APIRouter, Depends, HTTPException
from . import schemas
from app.core.dependencies import get_todo_service, get_current_user
from app.modules.ai_chat.vector_store import upsert_todo, delete_todo as chroma_delete_todo
router = APIRouter()

@router.get("/", response_model=list[schemas.Todo])
def read_todos(skip: int = 0, limit: int = 100, current_user=Depends(get_current_user), todo_service=Depends(get_todo_service)):
    return todo_service.get_todos_by_user(current_user.id, skip, limit)

@router.post("/", response_model=schemas.Todo)
def create_todo(todo: schemas.TodoCreate, current_user=Depends(get_current_user), todo_service=Depends(get_todo_service)):
    db_todo = todo_service.create_todo(todo, current_user.id)
    upsert_todo(current_user.id, db_todo.id, db_todo.title, db_todo.description, db_todo.is_completed, db_todo.col, db_todo.priority, db_todo.tag)
    return db_todo

@router.get("/{todo_id}", response_model=schemas.Todo)
def read_todo(todo_id: int, current_user=Depends(get_current_user), todo_service=Depends(get_todo_service)):
    todo = todo_service.get_todo(todo_id)
    if todo is None or todo.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Todo not found")
    return todo

@router.put("/{todo_id}", response_model=schemas.Todo)
def update_todo(todo_id: int, todo_update: schemas.TodoUpdate, current_user=Depends(get_current_user), todo_service=Depends(get_todo_service)):
    todo = todo_service.get_todo(todo_id)
    if todo is None or todo.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Todo not found")
    updated = todo_service.update_todo(todo_id, todo_update)
    upsert_todo(current_user.id, updated.id, updated.title, updated.description, updated.is_completed, updated.col, updated.priority, updated.tag)
    return updated


@router.delete("/{todo_id}")
def delete_todo(todo_id: int, current_user=Depends(get_current_user), todo_service=Depends(get_todo_service)):
    todo = todo_service.get_todo(todo_id)
    if todo is None or todo.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Todo not found")
    success = todo_service.delete_todo(todo_id)
    chroma_delete_todo(current_user.id, todo_id)
    if not success:
        raise HTTPException(status_code=500, detail="Failed to delete todo")
    return {"message": "Todo deleted"}
