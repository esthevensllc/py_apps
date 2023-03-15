class NotificationService:
    def __init__(self, db):
        self.db = db

    def send_notification(self, subject, message, p_group):
        params = {'subject': subject, 'message': message, 'p_group': p_group}
        self.db.callproc("sp_send_mail_notification(:subject, :message, :p_group)", params)