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