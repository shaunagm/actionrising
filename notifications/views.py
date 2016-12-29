from django.views import generic
from django.contrib.auth.mixins import UserPassesTestMixin,  LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.core.urlresolvers import reverse

from actions.models import Action, Slate
from notifications.models import NotificationSettings
from notifications.lib.notification_handlers import send_non_user_notifications

class SettingsEditView(UserPassesTestMixin, generic.UpdateView):
    model = NotificationSettings
    template_name = "notifications/settings_form.html"
    fields = ['daily_action', 'use_own_actions_if_exist', 'if_followed', 'if_slate_followed',
        'if_comments_on_my_actions', 'if_actions_followed', 'if_my_actions_added_to_slate',
        'if_suggested_action', 'if_followed_users_create', 'if_followed_slates_updated']

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
        form.fields['if_slate_followed'].label = "Let me know when someone follows one of my slates"
        form.fields['if_actions_followed'].label = "Let me know when someone is taking " \
            + "one of my actions"
        form.fields['if_comments_on_my_actions'].label = "Let me know when someone comments on my action"
        form.fields['if_my_actions_added_to_slate'].label = "Let me know when someone adds "\
            + "an action I created to a slate"
        form.fields['if_suggested_action'].label = "Let me know when someone suggests " \
            + "I take an action"
        form.fields['if_followed_users_create'].label = "Let me know when a user I follow " \
            + "creates an action or slate"
        form.fields['if_followed_slates_updated'].label = "Let me know when a slate I follow " \
            + "gets a new action added to it"
        return form

@login_required
def nonuser_notification(request):
    if request.method == 'POST':

        pk = request.POST.get('pk');
        model = request.POST.get('model');
        message = request.POST.get('message');

        emails = []
        for i in range(0,6):
            email = request.POST.get('email' + str(i))
            if email and email != "":
                emails.append(email)

        if model == "Action":
            obj = Action.objects.get(pk=pk)
        elif model == "Slate":
            obj = Slate.objects.get(pk=pk)

        if obj:
            send_non_user_notifications(request.user, emails, message, obj)

    if model == "Action":
        return HttpResponseRedirect(reverse('action', kwargs={'slug':obj.slug}))
    elif model == "Slate":
        return HttpResponseRedirect(reverse('slate', kwargs={'slug':obj.slug}))
    else:
        return render(request, 'mysite/landing.html')
