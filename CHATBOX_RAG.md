# Hướng Dẫn Tích Hợp AI Chatbox với RAG + ChromaDB

## Tổng Quan

Tính năng chatbox cho phép user hỏi AI về các todo của mình.
AI sẽ dùng RAG (Retrieval-Augmented Generation) để lấy context từ database thông qua ChromaDB trước khi trả lời.

**Luồng hoạt động:**
```
User gửi câu hỏi
    → Embed câu hỏi thành vector
    → Tìm todos liên quan trong ChromaDB (similarity search)
    → Ghép todos tìm được vào prompt
    → Gửi prompt + context lên OpenAI
    → Trả về câu trả lời
```

## Cấu Trúc Thêm Vào

```
src/app/modules/
└── chat/
    ├── router.py       # POST /chat
    ├── service.py      # RAG logic
    ├── schemas.py      # Request/Response schemas
    └── vector_store.py # ChromaDB operations
```

---

## Bước 1: Cài Đặt Dependencies

```bash
pip install openai chromadb
```

Thêm vào `requirements.txt`:
```
openai==1.30.0
chromadb==0.5.0
```

Thêm vào `.env`:
```
OPENAI_API_KEY=sk-...
```

Thêm vào `config.py`:
```python
openai_api_key: str
```

---

## Bước 2: Vector Store (`src/app/modules/chat/vector_store.py`)

ChromaDB lưu vector locally, mỗi user có 1 collection riêng.

```python
import chromadb
from openai import OpenAI
from app.core.config import settings

chroma_client = chromadb.PersistentClient(path="./chroma_db")
openai_client = OpenAI(api_key=settings.openai_api_key)

def get_embedding(text: str) -> list[float]:
    response = openai_client.embeddings.create(
        input=text,
        model="text-embedding-3-small"
    )
    return response.data[0].embedding

def get_collection(user_id: int):
    return chroma_client.get_or_create_collection(name=f"user_{user_id}_todos")

def upsert_todo(user_id: int, todo_id: int, title: str, description: str, is_completed: bool):
    collection = get_collection(user_id)
    text = f"Title: {title}. Description: {description or ''}. Status: {'completed' if is_completed else 'pending'}"
    embedding = get_embedding(text)
    collection.upsert(
        ids=[str(todo_id)],
        embeddings=[embedding],
        documents=[text],
        metadatas=[{"todo_id": todo_id, "is_completed": is_completed}]
    )

def delete_todo(user_id: int, todo_id: int):
    collection = get_collection(user_id)
    collection.delete(ids=[str(todo_id)])

def search_todos(user_id: int, query: str, n_results: int = 5) -> list[str]:
    collection = get_collection(user_id)
    if collection.count() == 0:
        return []
    query_embedding = get_embedding(query)
    results = collection.query(embeddings=[query_embedding], n_results=n_results)
    return results["documents"][0] if results["documents"] else []
```

---

## Bước 3: Schemas (`src/app/modules/chat/schemas.py`)

```python
from pydantic import BaseModel

class ChatRequest(BaseModel):
    message: str

class ChatResponse(BaseModel):
    reply: str
```

---

## Bước 4: Service (`src/app/modules/chat/service.py`)

```python
from openai import OpenAI
from app.core.config import settings
from .vector_store import search_todos

openai_client = OpenAI(api_key=settings.openai_api_key)

def chat_with_ai(user_id: int, message: str) -> str:
    # Bước 1: Tìm todos liên quan
    relevant_todos = search_todos(user_id, message)

    # Bước 2: Tạo context từ todos tìm được
    if relevant_todos:
        context = "Danh sách công việc liên quan của user:\n" + "\n".join(
            f"- {doc}" for doc in relevant_todos
        )
    else:
        context = "User chưa có công việc nào."

    # Bước 3: Gửi lên OpenAI với context
    response = openai_client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "system",
                "content": (
                    "Bạn là trợ lý quản lý công việc. "
                    "Dựa vào danh sách công việc của user để trả lời. "
                    f"\n\n{context}"
                )
            },
            {"role": "user", "content": message}
        ]
    )
    return response.choices[0].message.content
```

---

## Bước 5: Router (`src/app/modules/chat/router.py`)

```python
from fastapi import APIRouter, Depends
from .schemas import ChatRequest, ChatResponse
from .service import chat_with_ai
from app.core.dependencies import get_current_user

router = APIRouter()

@router.post("/", response_model=ChatResponse)
def chat(request: ChatRequest, current_user=Depends(get_current_user)):
    reply = chat_with_ai(current_user.id, request.message)
    return ChatResponse(reply=reply)
```

---

## Bước 6: Đồng Bộ ChromaDB Khi Todo Thay Đổi

Mỗi khi user tạo/sửa/xóa todo, cần cập nhật ChromaDB. Sửa `todos/router.py`:

```python
from app.modules.chat.vector_store import upsert_todo, delete_todo

@router.post("/", response_model=schemas.Todo)
def create_todo(todo: schemas.TodoCreate, current_user=Depends(get_current_user), todo_service=Depends(get_todo_service)):
    db_todo = todo_service.create_todo(todo, current_user.id)
    upsert_todo(current_user.id, db_todo.id, db_todo.title, db_todo.description, db_todo.is_completed)
    return db_todo

@router.put("/{todo_id}", response_model=schemas.Todo)
def update_todo(todo_id: int, todo_update: schemas.TodoUpdate, current_user=Depends(get_current_user), todo_service=Depends(get_todo_service)):
    todo = todo_service.get_todo(todo_id)
    if todo is None or todo.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Todo not found")
    updated = todo_service.update_todo(todo_id, todo_update)
    upsert_todo(current_user.id, updated.id, updated.title, updated.description, updated.is_completed)
    return updated

@router.delete("/{todo_id}")
def delete_todo_route(todo_id: int, current_user=Depends(get_current_user), todo_service=Depends(get_todo_service)):
    todo = todo_service.get_todo(todo_id)
    if todo is None or todo.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Todo not found")
    todo_service.delete_todo(todo_id)
    delete_todo(current_user.id, todo_id)
    return {"message": "Todo deleted"}
```

---

## Bước 7: Sync Todos Hiện Có Vào ChromaDB

Nếu user đã có todos từ trước, cần sync vào ChromaDB 1 lần. Thêm endpoint admin hoặc chạy script:

```python
# scripts/sync_chroma.py
import sys
sys.path.insert(0, "./src")

from app.core.database import SessionLocal
from app.modules.todos.models import Todo
from app.modules.chat.vector_store import upsert_todo

db = SessionLocal()
todos = db.query(Todo).all()
for todo in todos:
    upsert_todo(todo.user_id, todo.id, todo.title, todo.description, todo.is_completed)
    print(f"Synced todo {todo.id}: {todo.title}")
db.close()
print("Done!")
```

Chạy:
```bash
python scripts/sync_chroma.py
```

---

## Bước 8: Đăng Ký Router

Thêm vào `src/app/api/v1/router.py`:

```python
from app.modules.chat.router import router as chat_router

router.include_router(chat_router, prefix="/chat", tags=["chat"])
```

---

## Bước 9: Thêm `chroma_db/` vào `.gitignore`

```
chroma_db/
```

---

## Test Với Postman

**1. Tạo vài todos trước:**
```
POST /api/v1/todos/
{
    "title": "Học FastAPI",
    "description": "Hoàn thành module authentication",
    "is_completed": false
}
```

**2. Chat với AI:**
```
POST /api/v1/chat/
Authorization: Bearer <token>
{
    "message": "Tôi còn những việc gì chưa làm?"
}
```

**Response:**
```json
{
    "reply": "Bạn còn 1 công việc chưa hoàn thành: 'Học FastAPI' - Hoàn thành module authentication."
}
```

---

## Lưu Ý

- `chroma_db/` được lưu local tại thư mục chạy uvicorn — khi deploy cần mount volume
- `text-embedding-3-small` rẻ hơn `ada-002` và chất lượng tốt hơn
- `gpt-4o-mini` rẻ hơn `gpt-4o` ~15 lần, đủ dùng cho todo app
- Mỗi user có 1 collection riêng trong ChromaDB → data isolation
