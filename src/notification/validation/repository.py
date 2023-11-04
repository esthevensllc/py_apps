import cx_Oracle

class OracleNotificationControlRepository:
    def __init__(self, db):
        self.db = db
        self.table = "padm_notification_control"

    def find_by_notification_id(self, notification_id):
        data = self.db.fetch(f"SELECT notification_id, name, last_validation, last_notification FROM {self.table} WHERE notification_id = {notification_id}")
        if len(data) > 0:
            row = data[0]
            return {"notification_id": row[0], "name": row[1], "last_validation": row[2], "last_notification": row[3]}
        return None

    def save(self, notification_id, name, last_notification):
        data = self.db.fetch(f"SELECT notification_id, name, last_validation, last_notification FROM {self.table} WHERE notification_id = {notification_id}")
        if (len(data) > 0):
            template = f"""UPDATE {self.table} SET
            name = :p_name,
            last_validation = SYSDATE,
            last_notification = TO_DATE(:last_notification, 'YYYY-MM-DD HH24:MI:SS')
            WHERE notification_id = :notification_id"""
            if last_notification is None:
                last_notification = data[0][3]
        else:
            template = f"""INSERT INTO {self.table}(notification_id, name, last_validation, last_notification)
            VALUES (:notification_id, :p_name, sysdate, TO_DATE(:last_notification, 'YYYY-MM-DD HH24:MI:SS'))"""
        config = {
            'template': template,
            'bindings': {
                "notification_id": cx_Oracle.NUMBER,
                "p_name": cx_Oracle.STRING,
                "last_notification": cx_Oracle.STRING,
            },
            'row_type': 'object',
            'limit_to_commit': 10
        }
        values = {
            "notification_id": notification_id,
            "p_name": name,
            "last_notification": None
        }
        if last_notification is not None:
            values["last_notification"] = last_notification.strftime("%Y-%m-%d %H:%M:%S")
        self.db.save_from_array2(config,[values])
