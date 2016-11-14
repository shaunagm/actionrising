from django.contrib import admin
from actions.models import Action, ActionType, ActionTopic, Slate, SlateActionRelationship

admin.site.register(Action)
admin.site.register(ActionType)
admin.site.register(ActionTopic)
admin.site.register(Slate)
admin.site.register(SlateActionRelationship)
