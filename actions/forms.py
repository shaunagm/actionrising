from django import forms
from datetimewidget.widgets import DateTimeWidget
from django.forms.widgets import HiddenInput

from actions.models import Action
from tags.lib import tag_helpers
from tags.models import Tag
from mysite.lib.choices import PRIVACY_CHOICES, TIME_CHOICES
from mysite.lib.privacy import get_global_privacy_default
from plugins import plugin_helpers

class ActionForm(forms.ModelForm):

    class Meta:
        model = Action
        fields = ['title', 'anonymize', 'description', 'privacy', 'priority', 'duration',
            'status', 'deadline']
        widgets = {
            'deadline': DateTimeWidget(options={'format': 'mm/dd/yyyy HH:mm'}, bootstrap_version=3),
        }
        help_texts = {
            'anonymize': 'Show "anonymous" as creator. (Note: this changes the display only, and you can change your mind and choose to show your username later.)',
            'deadline': 'MM/DD/YYYY HH:MM:SS (hours, minutes and seconds optional, defaults to midnight)'
            }

    def __init__(self, user, formtype, *args, **kwargs):
        super(ActionForm, self).__init__(*args, **kwargs)
        self.user = user
        self.formtype = formtype
        if self.formtype == "create":
            self.fields['status'].widget = HiddenInput()

        # Set privacy
        NEW_CHOICES = (PRIVACY_CHOICES[0], PRIVACY_CHOICES[1], PRIVACY_CHOICES[2], ('inh', get_global_privacy_default(user.profile, "decorated")))
        self.fields['privacy'].choices = NEW_CHOICES

        # Set tags
        self.fields = tag_helpers.add_tag_fields_to_form(self.fields, self.instance, formtype)

        # Set plugin fields
        self = plugin_helpers.add_plugin_fields(self)

    def save(self, commit=True):
        instance = super(ActionForm, self).save(commit=False)

        # Add user if created, then save
        if self.formtype == "create":
            instance.creator = self.user
        instance.save()

        # Handle tags
        tags, form = tag_helpers.get_tags_from_valid_form(self)
        tag_helpers.add_tags_to_object(instance, tags)

        # Handle plugins
        plugin_helpers.process_plugin_fields(self, instance)

        return instance


### ALL filter results calls are given the request?

class FilterWizard_Kind(forms.Form):
    question = "What kinds of actions do you want to hear about?"
    kinds = forms.ModelMultipleChoiceField(queryset=Tag.objects.filter(kind="type"),
        required=False, label='')

    def update_filter(self, actionfilter, request):
        if 'kinds' in request.POST and request.POST['kinds']:
            actionfilter.set_kinds(request.POST.getlist('kinds'))

class FilterWizard_Topic(forms.Form):
    question = "What topics are you most interested in?"
    topics = forms.ModelMultipleChoiceField(queryset=Tag.objects.filter(kind="topic"),
        required=False, label='')

    def update_filter(self, actionfilter, request):
        if 'topics' in request.POST and request.POST['topics']:
            actionfilter.set_topics(request.POST.getlist('topics'))

class FilterWizard_Time(forms.Form):
    question = "How much time can you spend on the action?"
    time = forms.MultipleChoiceField(choices=TIME_CHOICES, required=False, label='',
        initial=(c[0] for c in TIME_CHOICES))

    def update_filter(self, actionfilter, request):
        if 'time' in request.POST and request.POST['time']:
            actionfilter.set_time(request.POST.getlist('time'))

class FilterWizard_Friends(forms.Form):
    question = "Should we only include actions created by people you follow?"
    override_template = "actions/filter_templates/friends_template.html"

    def __init__(self, request, *args, **kwargs):
        super(FilterWizard_Friends, self).__init__(*args, **kwargs)
        friends = [(user, user) for user in request.user.profile.get_people_tracking()]
        if len(friends) < 10:
            if not friends: # if 0 friends
                self.warning = """You don't follow anyone, which means choosing 'yes' will
                    eliminate all actions. <br />Why not <a target='_blank' href='/profiles/profiles'>
                    add some friends</a>?"""
            else:
                people_statement = "only 1 person" if len(friends) == 1 else "only %s people" % len(friends)
                self.warning = """You follow %s, which means choosing 'yes' will drastically
                    limit available actions. <br />Why not <a target='_blank' href='/profiles/profiles'>
                    add more friends</a>?""" % people_statement

    def update_filter(self, actionfilter, request):
        if 'friends_yes' in request.POST:
            actionfilter.friends = True
            actionfilter.save()
