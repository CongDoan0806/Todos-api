from fastapi import APIRouter
from app.modules.users.router import router as user_router
from app.modules.todos.router import router as todo_router
from app.modules.notifications.router import router as notification_router

router = APIRouter()

router.include_router(user_router, prefix="/auth", tags=["authentication"])
router.include_router(todo_router, prefix="/todos", tags=["todos"])
router.include_router(notification_router, prefix="/notifications", tags=["notifications"])