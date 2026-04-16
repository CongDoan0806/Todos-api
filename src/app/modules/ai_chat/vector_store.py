import chromadb
from openai import OpenAI
from app.core.config import settings

chroma_client = chromadb.PersistentClient(path="./chroma_db")
openai_client = OpenAI(api_key=settings.openai_api_key)

def get_embedding(text: str) ->  list[float]:
    response = openai_client.embeddings.create(input=text, model="text-embedding-3-small")
    return response.data[0].embedding

def get_collection(user_id: int):
    return chroma_client.get_or_create_collection(name=f"user_{user_id}_collection")

def upsert_todo(user_id: int, todo_id: int, title: str, description: str, is_completed: bool, col: str = "todo", priority: str = "medium", tag: str = None):
    collection = get_collection(user_id)
    text = f"Title: {title}. Description: {description or ''}. Status: {'completed' if is_completed else 'pending'}. Column: {col}. Priority: {priority}. Tag: {tag or 'none'}."
    embedding = get_embedding(text)
    collection.upsert(
        ids=[str(todo_id)],
        embeddings=[embedding],
        documents=[text],
        metadatas=[{"todo_id": todo_id, "is_completed": is_completed, "col": col, "priority": priority, "tag": tag or ""}]
    )

def delete_todo(user_id: int, todo_id: int):
    collection = get_collection(user_id)
    collection.delete(ids=[str(todo_id)])

def search_todos(user_id: int, query: str, top_k: int = 5):
    collection = get_collection(user_id)
    query_embedding = get_embedding(query)
    results = collection.query(query_embeddings=[query_embedding], n_results=top_k)
    return results