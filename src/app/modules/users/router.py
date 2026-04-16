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