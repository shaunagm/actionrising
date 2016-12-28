from __future__ import unicode_literals

from django.apps import AppConfig


class ProfilesConfig(AppConfig):
    name = 'profiles'

    def ready(self):
        from actstream import registry
        import profiles.signals
        registry.register(self.get_model('Profile'))
        registry.register(self.get_model('ProfileActionRelationship'))
        registry.register(self.get_model('ProfileSlateRelationship'))
        registry.register(self.get_model('Relationship'))
        from django.contrib.auth.models import User
        registry.register(User)
        from django_comments.models import Comment
        registry.register(Comment)
