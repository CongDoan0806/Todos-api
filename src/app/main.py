from fastapi import FastAPI
from .api.v1.router import router
from .core.database import engine
from .modules.users.models import User
from .modules.todos.models import Todo

# Tạo tables
User.__table__.create(bind=engine, checkfirst=True)
Todo.__table__.create(bind=engine, checkfirst=True)

app = FastAPI(title="Todo API", version="1.0.0")

app.include_router(router, prefix="/api/v1")

@app.get("/")
def read_root():
    return {"message": "Welcome to Todo API"}