from itertools import chain

from django.shortcuts import render, redirect
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.views import generic
from django.contrib.auth.mixins import UserPassesTestMixin,  LoginRequiredMixin
from django.contrib.auth.decorators import login_required

from flags.lib.flag_helpers import get_user_flag_if_exists
from mysite.lib.choices import PrivacyChoices, StatusChoices
from mysite.lib.privacy import (check_privacy, filter_list_for_privacy,
    filter_list_for_privacy_annotated)
from profiles.lib.trackers import get_tracker_data_for_action
from tags.lib import tag_helpers
from actions.models import Action, ActionFilter
from actions import forms
from plugins import plugin_helpers

@login_required
def index(request):
    return HttpResponseRedirect(reverse('actions'))

class ActionView(UserPassesTestMixin, generic.DetailView):
    template_name = 'actions/action.html'
    model = Action

    def get(self, request, *args, **kwargs):
        # Check if this is a special action and, if so, redirect
        action = self.get_object()
        if action.special_action:
            name = action.special_action.split("_")[0] + "_action"
            return redirect(name, slug=action.slug)
        else:
            return super(ActionView, self).get(request, *args, **kwargs)

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
    queryset = Action.objects.filter(status__in=[StatusChoices.ready, StatusChoices.finished]).filter(current_privacy__in=[PrivacyChoices.public, PrivacyChoices.sitewide])

    def get_context_data(self, **kwargs):
        context = super(ActionListView, self).get_context_data(**kwargs)
        context['your_filters'] = self.request.user.actionfilter_set.all().order_by('date_created')
        print context
        return context

class PublicActionListView(generic.ListView):
    template_name = "actions/actions.html"
    model = Action
    queryset = Action.objects.filter(status__in=[StatusChoices.ready, StatusChoices.finished]).filter(current_privacy=PrivacyChoices.public)

class ActionCreateView(LoginRequiredMixin, generic.edit.CreateView):
    model = Action
    form_class = forms.ActionForm

    def get(self, request, *args, **kwargs):
        if not request.user.profile.verified and len(request.user.action_set.all()) > 10:
            return render(request, 'invites/verification_limit.html', {'actions': True})
        else:
            return super(ActionCreateView, self).get(request, *args, **kwargs)

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

    def get(self, request, *args, **kwargs):
        # Check if this is a special action and, if so, redirect
        action = self.get_object()
        if action.special_action:
            name = "edit_" + action.special_action.split("_")[0] + "_action"
            return redirect(name, slug=action.slug)
        else:
            return super(ActionEditView, self).get(request, *args, **kwargs)

    def test_func(self):
        obj = self.get_object()
        return obj.creator == self.request.user

    def get_form_kwargs(self):
        form_kws = super(ActionEditView, self).get_form_kwargs()
        form_kws["user"] = self.request.user
        form_kws["formtype"] = "update"
        return form_kws

@login_required
def keep_actions_open_view(request, pk):
    action = Action.objects.get(pk=pk)
    if action.creator == request.user or request.user.is_staff:
        action.keep_action_open()
        return render(request, 'actions/keep_open.html', context={'action': action })
    else:
        return HttpResponseRedirect(reverse('actions'))


class FindActionsLandingView(LoginRequiredMixin, generic.TemplateView):
    template_name = "actions/find_actions.html"

class CreateActionsLandingView(LoginRequiredMixin, generic.TemplateView):
    template_name = "actions/create_actions.html"

def filter_wizard_forms(request):
    form_list = [forms.FilterWizard_Kind(), forms.FilterWizard_Topic(),
        forms.FilterWizard_Time(), forms.FilterWizard_Friends(request)]
    plugin_forms = plugin_helpers.get_filter_forms_for_plugins(request)
    for index, form in enumerate(plugin_forms):
        form_list.append(form)
    return form_list

def process_filter_wizard_forms(request):
    results = []
    actionfilter = ActionFilter.objects.create(creator=request.user)
    for form in filter_wizard_forms(request):
        form.update_filter(actionfilter, request)
    return actionfilter

def filter_wizard_view(request):
    if request.method == 'POST':
        actionfilter = process_filter_wizard_forms(request)
        return redirect('filter', pk=actionfilter.pk)
    else:
        forms = filter_wizard_forms(request)
        return render(request, 'actions/filter_wizard.html', context={'forms': forms })

class ActionFilterView(UserPassesTestMixin, generic.DetailView):
    template_name = 'actions/filter_wizard_results.html'
    model = ActionFilter

    def get_context_data(self, **kwargs):
        context = super(ActionFilterView, self).get_context_data(**kwargs)
        context['actions'] = self.get_object().filter_actions()
        return context

    def test_func(self):
        '''Don't display unless user owns Filter'''
        obj = self.get_object()
        return obj.creator == self.request.user

def filter_save_status(request, pk, save_or_delete):
    actionfilter = ActionFilter.objects.get(pk=pk)
    if actionfilter.creator == request.user:
        if save_or_delete == "save":
            actionfilter.saved = True
        if save_or_delete == "delete":
            actionfilter.saved = False
        actionfilter.save()
    return redirect('filter', pk=actionfilter.pk)

class SlateRedirectView(generic.base.RedirectView):
    permanent = False
    query_string = True
    pattern_name = 'slate'
