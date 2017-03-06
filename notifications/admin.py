from django.contrib import admin
from django import forms

from notifications.models import (NotificationSettings, Notification, DailyActionSettings,
    GenericEmail)

admin.site.register(NotificationSettings)
admin.site.register(Notification)
admin.site.register(DailyActionSettings)

class GenericEmailAdmin(admin.ModelAdmin):

    def formfield_for_dbfield(self, db_field, **kwargs):
        formfield = super(GenericEmailAdmin, self).formfield_for_dbfield(db_field, **kwargs)
        if db_field.name == 'plain_body':
            formfield.widget = forms.Textarea(attrs={'cols': 80, 'rows': 20})
        return formfield

admin.site.register(GenericEmail, GenericEmailAdmin)
