import re

from django.forms import ModelForm, CharField, PasswordInput, TextInput
from django.contrib.auth.models import User
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.core.urlresolvers import reverse
from django.core.exceptions import ValidationError

from mysite.settings import PRODUCTION_DOMAIN
from notifications.lib.email_handlers import request_email
from accounts.lib.tokens import account_activation_token

class SignUpForm(ModelForm):
    password = CharField(widget=PasswordInput)

    class Meta:
        model = User
        fields = ['email', 'username', 'password']
        widgets = {
            'username': TextInput(
                attrs={'placeholder': "Characters, numbers, hyphens and dashes only"}),
            }

    def __init__(self, *args, **kwargs):
        super(SignUpForm, self).__init__(*args, **kwargs)
        self.fields['email'].required = True
        self.fields['username'].help_text = None

    def clean_email(self):
        '''Makes sure email is unique'''
        email = self.cleaned_data['email']
        if User.objects.filter(email=email).exists():
            raise ValidationError("Email already exists")
        return email

    def clean_username(self):
        '''Makes sure username is unique and has only valid characters'''
        username = self.cleaned_data['username']
        if User.objects.filter(username__iexact=username).exists():
            raise ValidationError("This username is already taken.")
        if not re.match(r'^[\w_-]+$', username):
            raise ValidationError("Enter a valid username. This value may contain only " \
                + "letters, numbers, hyphens and dashes.")
        return username

    def save(self, commit=True):
        instance = super(SignUpForm, self).save(commit=False)
        instance.is_active = False
        instance.save()

        # Send notification email with one-time token
        uidb64 = urlsafe_base64_encode(force_bytes(instance.pk))
        token = account_activation_token.make_token(instance)
        confirmation_url = PRODUCTION_DOMAIN + reverse('sign-up-confirmation',
            kwargs={'uidb64': uidb64, 'token': token})
        request_email(instance, confirmation_url)

        return instance
