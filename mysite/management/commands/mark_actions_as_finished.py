import datetime
from django.core.management.base import BaseCommand, CommandError
from actions.models import Action


class Command(BaseCommand):

    def handle(self, *args, **options):
        try:
            actions = Action.objects.filter(status="rea")
            for action in actions:
                if action.deadline < datetime.datetime.now():
                    action.status = 'fin'
                    action.save()
            print("Actions marked as finished")
        except:
            raise CommandError("Failure marking actions as finished")
