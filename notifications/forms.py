from django.forms import ModelForm, MultipleChoiceField
from mysite.lib.choices import TIME_CHOICES

from actions.models import ActionTopic, ActionType
from notifications.models import DailyActionSettings

ACTION_TYPE_CHOICES = [(i.pk, i.name) for i in ActionType.objects.all()]
ACTION_TOPIC_CHOICES = [(i.pk, i.name) for i in ActionTopic.objects.all()]

class DailyActionForm(ModelForm):
    duration_filter = MultipleChoiceField(choices=TIME_CHOICES, required=False)
    action_type_filter = MultipleChoiceField(choices=ACTION_TYPE_CHOICES, required=False)
    action_topic_filter = MultipleChoiceField(choices=ACTION_TOPIC_CHOICES, required=False)

    class Meta:
        model = DailyActionSettings
        fields = ['my_own_actions', 'my_friends_actions', 'popular_actions',
            'duration_filter', 'duration_filter_on', 'action_type_filter',
            'action_type_filter_on', 'action_topic_filter', 'action_topic_filter_on']

    def __init__(self, *args, **kwargs):
        super(DailyActionForm, self).__init__(*args, **kwargs)
