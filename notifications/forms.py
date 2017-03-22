from django.forms import ModelForm, MultipleChoiceField
from mysite.lib.choices import TimeChoices

from tags.models import Tag
from notifications.models import DailyActionSettings

class DailyActionForm(ModelForm):
    duration_filter = MultipleChoiceField(choices=TimeChoices.choices, required=False)
    tag_filter = MultipleChoiceField(choices=[(0,0)], required=False)

    class Meta:
        model = DailyActionSettings
        fields = ['my_own_actions', 'my_friends_actions', 'popular_actions',
            'duration_filter', 'duration_filter_on', 'tag_filter', 'tag_filter_on']

    def __init__(self, *args, **kwargs):
        super(DailyActionForm, self).__init__(*args, **kwargs)
        self.fields['tag_filter'].choices = [(i.pk, i.name) for i in Tag.objects.all()]
