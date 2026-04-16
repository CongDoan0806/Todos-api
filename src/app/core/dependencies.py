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

def get_notification_service(db: Session = Depends(get_db)):
    from app.modules.notifications.repository import NotificationRepository
    from app.modules.notifications.service import NotificationService
    repository = NotificationRepository(db)
    return NotificationService(repository)

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