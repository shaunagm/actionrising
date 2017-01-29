from itertools import chain

from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.views import generic
from django.contrib.auth.mixins import UserPassesTestMixin,  LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from formtools.wizard.views import SessionWizardView

from flags.lib.flag_helpers import get_user_flag_if_exists
from mysite.lib.privacy import (check_privacy, filter_list_for_privacy,
    filter_list_for_privacy_annotated)
from profiles.lib.trackers import get_tracker_data_for_action
from tags.lib import tag_helpers
from actions.models import Action
from actions import forms

@login_required
def index(request):
    return HttpResponseRedirect(reverse('actions'))

class ActionView(UserPassesTestMixin, generic.DetailView):
    template_name = 'actions/action.html'
    model = Action

    def get_context_data(self, **kwargs):
        context = super(ActionView, self).get_context_data(**kwargs)
        context['tag_list'] = self.object.get_tags()
        context['tracker_data'] = get_tracker_data_for_action(self.object, self.request.user)
        if self.request.user.is_authenticated():
            context['par'] = self.request.user.profile.get_par_given_action(self.object)
        context['flag'] = get_user_flag_if_exists(self.object, self.request.user)
        return context

    def test_func(self):
        obj = self.get_object()
        return check_privacy(obj, self.request.user)

class ActionListView(LoginRequiredMixin, generic.ListView):
    template_name = "actions/actions.html"
    model = Action
    queryset = Action.objects.filter(status__in=["rea", "fin"]).filter(current_privacy__in=["pub", "sit"])

class PublicActionListView(generic.ListView):
    template_name = "actions/actions.html"
    model = Action
    queryset = Action.objects.filter(status__in=["rea", "fin"]).filter(current_privacy="pub")

class ActionCreateView(LoginRequiredMixin, generic.edit.CreateView):
    model = Action
    form_class = forms.ActionForm

    def get_form_kwargs(self):
        form_kws = super(ActionCreateView, self).get_form_kwargs()
        form_kws["user"] = self.request.user
        form_kws["formtype"] = "create"
        return form_kws

    def get_success_url(self, **kwargs):
        return self.object.get_absolute_url()

class ActionEditView(UserPassesTestMixin, generic.edit.UpdateView):
    model = Action
    form_class = forms.ActionForm

    def test_func(self):
        obj = self.get_object()
        return obj.creator == self.request.user

    def get_form_kwargs(self):
        form_kws = super(ActionEditView, self).get_form_kwargs()
        form_kws["user"] = self.request.user
        form_kws["formtype"] = "update"
        return form_kws

class FindActionsLandingView(LoginRequiredMixin, generic.TemplateView):
    template_name = "actions/find_actions.html"

class CreateActionsLandingView(LoginRequiredMixin, generic.TemplateView):
    template_name = "actions/create_actions.html"

class ActionLearnView(LoginRequiredMixin, generic.TemplateView):
    template_name = "actions/learn.html"

def stop_early(wizard):
    # Bit of a hack, since you have to set the 'skip' condition for each step.
    for step in range(0,6):
        cleaned_data = wizard.get_cleaned_data_for_step(str(step))
        print(cleaned_data)
        # If thing return false
    return True

class FilterWizard(SessionWizardView):
    template_name = "actions/filter_wizard.html"
    form_list = [forms.FilterWizard_Kind, forms.FilterWizard_Topic, forms.FilterWizard_Time,
        forms.FilterWizard_Deadline, forms.FilterWizard_Location, forms.FilterWizard_Friends]
    condition_dict = dict.fromkeys([str(i) for i in range(0,6)], stop_early)

    def done(self, form_list, **kwargs):
        results = []
        for form in form_list:
            results = form.filter_results(self, results)
        return render(self.request, 'actions/wizard_results.html', { 'results': results })

class SlateRedirectView(generic.base.RedirectView):
    permanent = False
    query_string = True
    pattern_name = 'slate'
