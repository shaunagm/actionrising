import datetime
from django.utils import timezone
from django.core.management.base import BaseCommand, CommandError
from actions.models import Action
from notifications.lib import email_handlers
from mysite.lib.choices import StatusChoices

class Command(BaseCommand):

    def handle(self, *args, **options):
        try:
            actions = Action.objects.filter(status=StatusChoices.ready)
            for action in actions:
                if action.deadline and action.deadline < datetime.datetime.now(timezone.utc):
                    action.status = StatusChoices.finished
                    action.save()
                else:
                    if action.get_days_til_close_action() == 47:  # 3 day warning
                        if action.creator.email:
                            email_handlers.close_action_warning_email(action.creator.profile, action)
                    if action.get_days_til_close_action() > 49:  # close
                        action.status =  StatusChoices.finished
                        action.save()
                        if action.creator.email:
                            email_handlers.close_action_email(action.creator.profile, action)
            print("Actions marked as finished")
        except:
            raise CommandError("Failure marking actions as finished")
