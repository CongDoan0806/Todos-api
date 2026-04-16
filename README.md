# Hướng Dẫn Xây Dựng Todo App API với FastAPI

## Tổng Quan

Hướng dẫn chi tiết để xây dựng một Todo App API sử dụng FastAPI với cấu trúc modular. Ứng dụng sẽ bao gồm quản lý người dùng (users) và công việc (todos), với authentication cơ bản.

## Cấu Trúc Dự Án

```
my_api/
├── src/
│   └── app/
│       ├── core/
│       │   ├── config.py       # Cấu hình ứng dụng (env vars)
│       │   ├── database.py     # Kết nối database
│       │   └── dependencies.py # Dependencies dùng chung (get_db, get_current_user)
│       ├── modules/
│       │   ├── users/
│       │   │   ├── router.py      # API endpoints cho users
│       │   │   ├── service.py     # Logic business cho users
│       │   │   ├── repository.py  # Tương tác database cho users
│       │   │   ├── models.py      # SQLAlchemy models cho users
│       │   │   └── schemas.py     # Pydantic schemas cho users
│       │   └── todos/
│       │       ├── router.py      # API endpoints cho todos
│       │       ├── service.py     # Logic business cho todos
│       │       ├── repository.py  # Tương tác database cho todos
│       │       ├── models.py      # SQLAlchemy models cho todos
│       │       ├── schemas.py     # Pydantic schemas cho todos
│       ├── api/
│       │   └── v1/
│       │       └── router.py   # Router chính include tất cả module routers
│       └── main.py            # FastAPI app instance
├── tests/                     # Thư mục chứa tests
├── .env                       # File cấu hình environment variables
├── requirements.txt           # Dependencies Python
└── alembic/                   # Database migrations
```

## Bước 1: Thiết Lập Môi Trường và Dependencies

### 1.1 Tạo Virtual Environment

```bash
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac
```

### 1.2 Cài Đặt Dependencies

Cập nhật `requirements.txt`:

```
fastapi==0.104.1
uvicorn[standard]==0.24.0
sqlalchemy==2.0.23
alembic==1.12.1
psycopg2-binary==2.9.9  # hoặc pymysql cho MySQL
python-dotenv==1.0.0
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
python-multipart==0.0.6
```

Cài đặt:

```bash
pip install -r requirements.txt
```

### 1.3 Cấu Hình Environment Variables

Cập nhật `.env`:

```
DATABASE_URL=postgresql://user:password@localhost/todo_db
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

## Bước 2: Cấu Hình Cơ Sở Dữ Liệu

### 2.1 Cấu Hình Database Connection (`src/app/core/database.py`)

```python
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from .config import settings

SQLALCHEMY_DATABASE_URL = settings.database_url

engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

### 2.2 Cấu Hình Settings (`src/app/core/config.py`)

```python
from pydantic import BaseSettings

class Settings(BaseSettings):
    database_url: str
    secret_key: str
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30

    class Config:
        env_file = ".env"

settings = Settings()
```

### 2.3 Khởi Tạo Alembic

```bash
alembic init alembic
```

Cập nhật `alembic.ini`:

```
sqlalchemy.url = driver://user:pass@localhost/dbname
```

Cập nhật `alembic/env.py`:

```python
from app.core.database import Base
target_metadata = Base.metadata
```

## Bước 3: Tạo Models (SQLAlchemy)

### 3.1 User Model (`src/app/modules/users/models.py`)

```python
from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.sql import func
from app.core.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
```

### 3.2 Todo Model (`src/app/modules/todos/models.py`)

```python
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.core.database import Base

class Todo(Base):
    __tablename__ = "todos"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    description = Column(String, nullable=True)
    completed = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    user_id = Column(Integer, ForeignKey("users.id"))

    owner = relationship("User", back_populates="todos")
```

Cập nhật User model để có relationship:

```python
# Trong users/models.py, thêm:
todos = relationship("Todo", back_populates="owner")
```

## Bước 4: Tạo Schemas (Pydantic)

### 4.1 User Schemas (`src/app/modules/users/schemas.py`)

```python
from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime

class UserBase(BaseModel):
    email: EmailStr
    username: str

class UserCreate(UserBase):
    password: str

class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    username: Optional[str] = None
    password: Optional[str] = None

class User(UserBase):
    id: int
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        orm_mode = True

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None
```

### 4.2 Todo Schemas (`src/app/modules/todos/schemas.py`)

```python
from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class TodoBase(BaseModel):
    title: str
    description: Optional[str] = None
    completed: bool = False

class TodoCreate(TodoBase):
    pass

class TodoUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    completed: Optional[bool] = None

class Todo(TodoBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime]
    user_id: int

    class Config:
        orm_mode = True
```

## Bước 5: Tạo Repositories

### 5.1 User Repository (`src/app/modules/users/repository.py`)

```python
from sqlalchemy.orm import Session
from . import models, schemas
from app.core.security import get_password_hash

class UserRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_user(self, user_id: int):
        return self.db.query(models.User).filter(models.User.id == user_id).first()

    def get_user_by_email(self, email: str):
        return self.db.query(models.User).filter(models.User.email == email).first()

    def get_user_by_username(self, username: str):
        return self.db.query(models.User).filter(models.User.username == username).first()

    def get_users(self, skip: int = 0, limit: int = 100):
        return self.db.query(models.User).offset(skip).limit(limit).all()

    def create_user(self, user: schemas.UserCreate):
        hashed_password = get_password_hash(user.password)
        db_user = models.User(
            email=user.email,
            username=user.username,
            hashed_password=hashed_password
        )
        self.db.add(db_user)
        self.db.commit()
        self.db.refresh(db_user)
        return db_user

    def update_user(self, user_id: int, user_update: schemas.UserUpdate):
        db_user = self.get_user(user_id)
        if db_user:
            update_data = user_update.dict(exclude_unset=True)
            if "password" in update_data:
                update_data["hashed_password"] = get_password_hash(update_data.pop("password"))
            for field, value in update_data.items():
                setattr(db_user, field, value)
            self.db.commit()
            self.db.refresh(db_user)
        return db_user

    def delete_user(self, user_id: int):
        db_user = self.get_user(user_id)
        if db_user:
            self.db.delete(db_user)
            self.db.commit()
        return db_user
```

### 5.2 Todo Repository (`src/app/modules/todos/repository.py`)

```python
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
        db_todo = models.Todo(**todo.dict(), user_id=user_id)
        self.db.add(db_todo)
        self.db.commit()
        self.db.refresh(db_todo)
        return db_todo

    def update_todo(self, todo_id: int, todo_update: schemas.TodoUpdate):
        db_todo = self.get_todo(todo_id)
        if db_todo:
            update_data = todo_update.dict(exclude_unset=True)
            for field, value in update_data.items():
                setattr(db_todo, field, value)
            self.db.commit()
            self.db.refresh(db_todo)
        return db_todo

    def delete_todo(self, todo_id: int):
        db_todo = self.get_todo(todo_id)
        if db_todo:
            self.db.delete(db_todo)
            self.db.commit()
        return db_todo
```

## Bước 6: Tạo Services

### 6.1 User Service (`src/app/modules/users/service.py`)

```python
from .repository import UserRepository
from . import schemas

class UserService:
    def __init__(self, repository: UserRepository):
        self.repository = repository

    def get_user(self, user_id: int):
        return self.repository.get_user(user_id)

    def get_user_by_email(self, email: str):
        return self.repository.get_user_by_email(email)

    def get_user_by_username(self, username: str):
        return self.repository.get_user_by_username(username)

    def get_users(self, skip: int = 0, limit: int = 100):
        return self.repository.get_users(skip, limit)

    def create_user(self, user: schemas.UserCreate):
        # Kiểm tra email/username đã tồn tại
        if self.repository.get_user_by_email(user.email):
            raise ValueError("Email already registered")
        if self.repository.get_user_by_username(user.username):
            raise ValueError("Username already registered")
        return self.repository.create_user(user)

    def update_user(self, user_id: int, user_update: schemas.UserUpdate):
        return self.repository.update_user(user_id, user_update)

    def delete_user(self, user_id: int):
        return self.repository.delete_user(user_id)
```

### 6.2 Todo Service (`src/app/modules/todos/service.py`)

```python
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
```

## Bước 7: Tạo Dependencies (`src/app/core/dependencies.py`)

```python
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from jose import JWTError, jwt
from .database import get_db
from .config import settings
from app.modules.users.repository import UserRepository
from app.modules.users.service import UserService

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

def get_user_service(db: Session = Depends(get_db)):
    repository = UserRepository(db)
    return UserService(repository)

def get_todo_service(db: Session = Depends(get_db)):
    from app.modules.todos.repository import TodoRepository
    from app.modules.todos.service import TodoService
    repository = TodoRepository(db)
    return TodoService(repository)

async def get_current_user(token: str = Depends(oauth2_scheme), user_service: UserService = Depends(get_user_service)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    user = user_service.get_user_by_username(username)
    if user is None:
        raise credentials_exception
    return user
```

## Bước 8: Tạo Routers

### 8.1 User Router (`src/app/modules/users/router.py`)

```python
from fastapi import APIRouter, Depends, HTTPException
from . import schemas
from app.core.dependencies import get_user_service, get_current_user
from app.core.security import verify_password, create_access_token

router = APIRouter()

@router.post("/register", response_model=schemas.User)
def register(user: schemas.UserCreate, user_service = Depends(get_user_service)):
    try:
        return user_service.create_user(user)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/login", response_model=schemas.Token)
def login(user_credentials: schemas.UserCreate, user_service = Depends(get_user_service)):
    user = user_service.get_user_by_email(user_credentials.email)
    if not user or not verify_password(user_credentials.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Incorrect email or password")
    
    access_token = create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/me", response_model=schemas.User)
def read_users_me(current_user: schemas.User = Depends(get_current_user)):
    return current_user

@router.put("/me", response_model=schemas.User)
def update_user_me(user_update: schemas.UserUpdate, current_user: schemas.User = Depends(get_current_user), user_service = Depends(get_user_service)):
    return user_service.update_user(current_user.id, user_update)
```

### 8.2 Todo Router (`src/app/modules/todos/router.py`)

```python
from fastapi import APIRouter, Depends, HTTPException
from . import schemas
from app.core.dependencies import get_todo_service, get_current_user

router = APIRouter()

@router.get("/", response_model=list[schemas.Todo])
def read_todos(skip: int = 0, limit: int = 100, current_user: schemas.User = Depends(get_current_user), todo_service = Depends(get_todo_service)):
    todos = todo_service.get_todos_by_user(current_user.id, skip, limit)
    return todos

@router.post("/", response_model=schemas.Todo)
def create_todo(todo: schemas.TodoCreate, current_user: schemas.User = Depends(get_current_user), todo_service = Depends(get_todo_service)):
    return todo_service.create_todo(todo, current_user.id)

@router.get("/{todo_id}", response_model=schemas.Todo)
def read_todo(todo_id: int, current_user: schemas.User = Depends(get_current_user), todo_service = Depends(get_todo_service)):
    todo = todo_service.get_todo(todo_id)
    if todo is None or todo.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Todo not found")
    return todo

@router.put("/{todo_id}", response_model=schemas.Todo)
def update_todo(todo_id: int, todo_update: schemas.TodoUpdate, current_user: schemas.User = Depends(get_current_user), todo_service = Depends(get_todo_service)):
    todo = todo_service.get_todo(todo_id)
    if todo is None or todo.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Todo not found")
    return todo_service.update_todo(todo_id, todo_update)

@router.delete("/{todo_id}")
def delete_todo(todo_id: int, current_user: schemas.User = Depends(get_current_user), todo_service = Depends(get_todo_service)):
    todo = todo_service.get_todo(todo_id)
    if todo is None or todo.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Todo not found")
    todo_service.delete_todo(todo_id)
    return {"message": "Todo deleted"}
```

## Bước 9: Tích Hợp API Router (`src/app/api/v1/router.py`)

```python
from fastapi import APIRouter
from app.modules.users.router import router as user_router
from app.modules.todos.router import router as todo_router

router = APIRouter()

router.include_router(user_router, prefix="/auth", tags=["authentication"])
router.include_router(todo_router, prefix="/todos", tags=["todos"])
```

## Bước 10: Tạo Main App (`src/app/main.py`)

```python
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
```

## Bước 11: Thêm Security Utils

Tạo file `src/app/core/security.py`:

```python
from datetime import datetime, timedelta
from jose import JWTError, jwt
from passlib.context import CryptContext
from .config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.access_token_expire_minutes)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)
    return encoded_jwt
```

## Bước 12: Chạy Ứng Dụng

### 12.1 Tạo Database Migration

```bash
alembic revision --autogenerate -m "Initial migration"
alembic upgrade head
```

### 12.2 Chạy Server

```bash
uvicorn src.app.main:app --reload
```

Truy cập http://localhost:8000/docs để xem API documentation.

## Bước 13: Testing

Tạo file test cơ bản trong `tests/test_main.py`:

```python
from fastapi.testclient import TestClient
from src.app.main import app

client = TestClient(app)

def test_read_main():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Welcome to Todo API"}
```

Chạy test:

```bash
pytest
```

## Lưu Ý Quan Trọng

1. **Security**: Mã hóa password, JWT tokens, validation inputs.
2. **Error Handling**: Sử dụng HTTPException cho errors.
3. **Database**: Sử dụng Alembic cho migrations.
4. **Dependencies**: Inject dependencies properly.
5. **Modular Structure**: Tách biệt concerns (models, schemas, repositories, services, routers).
6. **Testing**: Viết unit tests và integration tests.
7. **Documentation**: Sử dụng FastAPI's automatic docs.

## Các Bước Tiếp Theo

1. Thêm validation nâng cao (email format, password strength).
2. Implement pagination cho danh sách todos.
3. Thêm search và filter cho todos.
4. Implement refresh tokens.
5. Thêm rate limiting.
6. Viết comprehensive tests.
7. Thêm logging và monitoring.
8. Containerize với Docker.
9. Deploy lên production.