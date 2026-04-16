from fastapi import APIRouter, Depends
from .schemas import ChatRequest, ChatResponse
from .service import chat_with_ai
from app.core.dependencies import get_current_user

router = APIRouter()

@router.post("/", response_model=ChatResponse)
def chat(request: ChatRequest, current_user=Depends(get_current_user)):
    result = chat_with_ai(current_user.id, request.message)
    return ChatResponse(**result)