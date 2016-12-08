from django.views import generic
from django.contrib.auth.mixins import UserPassesTestMixin,  LoginRequiredMixin

from notifications.models import NotificationSettings

class SettingsEditView(UserPassesTestMixin, generic.UpdateView):
    model = NotificationSettings
    template_name = "notifications/settings_form.html"
    fields = ['daily_action', 'use_own_actions_if_exist', 'if_followed', 'if_comments_on_my_actions',
        'if_actions_followed', 'if_my_actions_added_to_slate']

    def test_func(self):
        obj = self.get_object()
        return obj.user == self.request.user

    def get_success_url(self, **kwargs):
        return self.request.user.profile.get_absolute_url()

    def get_form(self):
        form = super(SettingsEditView, self).get_form()
        form.fields['daily_action'].label = "Send me an action every day"
        form.fields['use_own_actions_if_exist'].label = "Choose the daily action "\
            + " from my open actions (default is an action from the top open actions "\
            + "on the site)"
        form.fields['if_followed'].label = "Let me know when someone follows me"
        form.fields['if_comments_on_my_actions'].label = "Let me know when someone comments on my action"
        form.fields['if_actions_followed'].label = "Let me know when someone adds "\
            + "an action I created to their list of actions"
        form.fields['if_my_actions_added_to_slate'].label = "Let me know when someone adds "\
            + "an action I created to a slate"
        return form
