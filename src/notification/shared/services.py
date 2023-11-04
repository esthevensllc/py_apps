import json
import requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

NOTIFICATION_CONFIG_REPO = 'src.notification.config.InMemoryNotificationConfigRepository'
NOTIFICATION_CONTROL_REPO = 'src.notification.validation.OracleNotificationControlRepository'
NOTIFICATION_VALIDATOR = 'src.notification.validation.NotificationValidator'

class NotificationAppProvider:
    def __init__(self, app_container):
        def notification_repo(self):
            from src.notification.config.repository import InMemoryNotificationConfigRepository
            return InMemoryNotificationConfigRepository(app_container.getInstance("dboracle"))
        app_container.bind(NOTIFICATION_CONFIG_REPO, notification_repo)

        def notification_repo(self):
            from src.notification.validation.repository import OracleNotificationControlRepository
            return OracleNotificationControlRepository(app_container.getInstance("dboracle"))
        app_container.bind(NOTIFICATION_CONTROL_REPO, notification_repo)

        def notification_validator(self):
            from src.notification.validation.services import NotificationValidator
            deps = app_container.getInstancesInArray([
                NOTIFICATION_CONFIG_REPO,
                "dboracle",
                "notification_service",
                NOTIFICATION_CONTROL_REPO
            ])
            return NotificationValidator(*deps)
        app_container.bind(NOTIFICATION_VALIDATOR, notification_validator)
