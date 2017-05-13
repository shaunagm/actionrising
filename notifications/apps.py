from __future__ import unicode_literals

from django.apps import AppConfig

class NotificationsConfig(AppConfig):
    name = 'notifications'

    def ready(self):
        # register signals
        from .lib import notification_handlers  # noqa
