from .repository import NotificationRepository
from . import schemas
class NotificationService:
    def __init__(self, repository: NotificationRepository):
        self.repository = repository

    def get_notifications(self, user_id:int):
        return self.repository.get_notifications(user_id)