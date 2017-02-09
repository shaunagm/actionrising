from __future__ import unicode_literals
from django.contrib.auth.models import User
from django.contrib.auth.backends import ModelBackend

# Thanks https://gist.github.com/tijs/7988341

class CustomModelBackend(ModelBackend):
    """
    Subclass the default ModelBackend
    """

    def authenticate(self, username=None, password=None, **kwargs):
        if username is None:
            username = kwargs.get(User.USERNAME_FIELD)
        try:
            # replace default lookup with case insensitive lookup
            user = User.objects.get(username__iexact=username)
            if user.check_password(password):
                return user
        except User.DoesNotExist:
            pass
