from fastapi import APIRouter, Depends, HTTPException
from . import schemas
from app.core.dependencies import get_notification_service, get_current_user

router = APIRouter()
@router.get("/notifications", response_model=list[schemas.NotificationBase])
def read_notifications(notification_service = Depends(get_notification_service), current_user = Depends(get_current_user)):
    return notification_service.get_notifications(current_user.id)