import datetime as dt
import requests
from jinja2 import Template
from src.notification.config.domain import NotificationConfig

class NotificationValidator:
    def __init__(self, repo: NotificationConfig, oracle, notification, notification_control_repo):
        self.repo = repo
        self.oracle = oracle
        self.notification = notification
        self.notification_control_repo = notification_control_repo

    def execute(self):
        validations = self.repo.get()
        for row in validations:
            self.execute_for(row)

    def execute_for(self, config):
        print(config["name"])
        data = []
        try:
            if config["type_id"] == "db":
                data = self.oracle.fetch(config["query"])
            elif config["type_id"] == "fetch":
                response = requests.get(config["api"])
                data = response.json()

            rule_result = "true"
            notify = False
            if config.get("rules") is not None:
                rule_template = Template(config["rules"])
                rule_result = rule_template.render({"data": data})
                notify = rule_result.strip() == "true"
            else:
                notify = len(data) > 0

            notification_date = None
            control = self.notification_control_repo.find_by_notification_id(config["id"])
            can_notify = True
            if control is not None:
                if control["last_notification"] is not None:
                    can_notify = (dt.datetime.now() - control["last_notification"]) >= dt.timedelta(minutes=config["range_minutes"])
            if notify and can_notify:
                print(f"->notify")
                message_template = Template(config["template"])
                message = message_template.render({"data": data})
                notification_date = dt.datetime.now()
                self.notification.send_notification(config["asunto"], message, config["group_id"])
            self.notification_control_repo.save(config["id"], config["name"], notification_date)
        except BaseException as e:
            print(f"->notify error")
            notification_date = dt.datetime.now()
            self.notification.send_notification(config["asunto"], str(e), config["group_id"])
            self.notification_control_repo.save(config["id"], config["name"], notification_date)




