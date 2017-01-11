from __future__ import unicode_literals

from django.apps import AppConfig


class ActionsConfig(AppConfig):
    name = 'actions'

    def ready(self):
        from actstream import registry
        import actions.signals
        registry.register(self.get_model('Action'))
