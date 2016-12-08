from django.contrib import admin

from notifications.models import NotificationSettings, Notification

admin.site.register(NotificationSettings)
admin.site.register(Notification)
