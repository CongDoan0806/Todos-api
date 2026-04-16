from fastapi import FastAPI
from .api.v1.router import router
from .core.database import engine
from .modules.users.models import User
from .modules.todos.models import Todo
from fastapi.middleware.cors import CORSMiddleware

User.__table__.create(bind=engine, checkfirst=True)
Todo.__table__.create(bind=engine, checkfirst=True)

app = FastAPI(title="Todo API", version="1.0.0")

app.include_router(router, prefix="/api/v1")
origins = [
    "http://localhost:3000",    
    "http://localhost:5173",    
    "http://127.0.0.1:3000",
    "http://127.0.0.1:5173",
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "Welcome to Todo API"}