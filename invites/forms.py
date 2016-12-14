from django.forms import ModelForm, Form, CharField
from django.contrib.auth.models import User
from datetimewidget.widgets import DateTimeWidget
from invites.models import Invite

class InviteForm(ModelForm):

    class Meta:
        model = Invite
        fields = ['username', 'email', 'reasoning']

    def __init__(self, *args, **kwargs):
        super(InviteForm, self).__init__(*args, **kwargs)
        self.fields['username'].label = "Desired username"
        self.fields['reasoning'].label = "Tell us a bit about yourself and why you " \
            "want an account.  We use this info to vet people and keep the site troll-free."

    def save(self, commit=True):
        self.instance.self_submitted = True
        user = User.objects.filter(email=self.instance.email)
        if user:
            self.instance.request_status = "duplicate"
        return super(InviteForm, self).save(commit=commit)

class InviteFriendForm(ModelForm):

    class Meta:
        model = Invite
        fields = ['email', 'reasoning']

    def __init__(self, *args, **kwargs):
        super(InviteFriendForm, self).__init__(*args, **kwargs)
        self.fields['email'].label = "What's your friend's email?"
        self.fields['reasoning'].label = "Tell us a bit about your friend and why they'd " \
            "like an account. We use this info to vet people and keep the site troll-free."

    def save(self, commit=True):
        user = User.objects.filter(email=self.instance.email)
        if user:
            self.instance.request_status = "duplicate"
        return super(InviteFriendForm, self).save(commit=commit)

class CreateUserFromInviteForm(Form):
    username = CharField(label='Username', max_length=20)
    password = CharField(label='Password', max_length=20)

    def save(self, email, commit=False):
        username = self.cleaned_data['username']
        password = self.cleaned_data['password']
        User.objects.create_user(username=username, email=email, password=password)
