from django.contrib import admin
from actions.models import Action, ActionType, ActionTopic

admin.site.register(Action)
admin.site.register(ActionType)
admin.site.register(ActionTopic)
