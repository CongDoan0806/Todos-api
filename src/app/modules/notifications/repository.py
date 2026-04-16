class NotificationRepository:
    def __init__(self, db):
        self.db = db
    def get_notifications(self, user_id: int):
        return self.db.query(models.Notification).filter(models.Notification.user_id == user_id).all()