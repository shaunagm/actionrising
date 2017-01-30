from django.forms import ModelForm, Form, CharField, EmailField, PasswordInput
from django.contrib.auth.models import User
from datetimewidget.widgets import DateTimeWidget
from invites.models import Invite

class SignUpForm(ModelForm):
    password = CharField(widget=PasswordInput)

    class Meta:
        model = Invite
        fields = ['username', 'password', 'email', 'reasoning']

    def __init__(self, *args, **kwargs):
        super(SignUpForm, self).__init__(*args, **kwargs)
        self.fields['username'].label = "Desired username"
        self.fields['reasoning'].label = "Tell us a bit about yourself and why you " \
            "want an account.  We use this info to vet people and keep the site troll-free."

    def save(self, commit=True):
        self.instance.self_submitted = True
        user = User.objects.create(username=self.instance.username, email=self.instance.email,
            is_active=False)
        user.set_password(self.cleaned_data['password'])
        user.save()
        return super(SignUpForm, self).save(commit=commit)
