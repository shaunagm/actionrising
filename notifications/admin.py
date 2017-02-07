from django.contrib import admin

from notifications.models import (NotificationSettings, Notification, DailyActionSettings,
    GenericEmail)

admin.site.register(NotificationSettings)
admin.site.register(Notification)
admin.site.register(DailyActionSettings)
admin.site.register(GenericEmail)
