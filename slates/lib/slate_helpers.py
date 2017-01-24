from slates.models import Slate, SlateActionRelationship

def manage_actions(formtype, instance, actions):
    if formtype == "create":
        for action in actions:
            SlateActionRelationship.objects.create(slate=instance, action=action)
    else:
        for action in actions:
            if action not in instance.actions.all():
                SlateActionRelationship.objects.create(slate=instance, action=action)
        for action in instance.actions.all():
            if action not in actions:
                sar = SlateActionRelationship.objects.get(slate=instance, action=action)
                sar.delete()
