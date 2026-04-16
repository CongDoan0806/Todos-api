from pydantic import BaseModel
from typing import Optional, Any

class ChatRequest(BaseModel):
    message: str

class SuggestedAction(BaseModel):
    action: str        # "create_todo" | "update_todo" | "delete_todo"
    todo_id: Optional[int] = None
    payload: Optional[dict[str, Any]] = None

class ChatResponse(BaseModel):
    answer: str
    suggested_action: Optional[SuggestedAction] = None