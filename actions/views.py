from itertools import chain

from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.views import generic
from django.contrib.auth.mixins import UserPassesTestMixin,  LoginRequiredMixin
from django.contrib.auth.decorators import login_required

from flags.lib.flag_helpers import get_user_flag_if_exists
from mysite.lib.privacy import (check_privacy, filter_list_for_privacy,
    filter_list_for_privacy_annotated)
from profiles.lib.trackers import get_tracker_data_for_action
from tags.lib import tag_helpers
from actions.models import Action
from actions.forms import ActionForm

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

def change_action_helper(form, user, create=False, change_loc=False):
    tags, form = tag_helpers.get_tags_from_valid_form(form)
    object = form.save(commit=False)
    if create:
        object.creator = user
    if change_loc:
        object.save(update_fields=['location'])
    else:
        object.save()
    tag_helpers.add_tags_to_object(object, tags)
    return object

class ActionCreateView(LoginRequiredMixin, generic.edit.CreateView):
    model = Action
    form_class = ActionForm

    def get_form_kwargs(self):
        form_kws = super(ActionCreateView, self).get_form_kwargs()
        form_kws["user"] = self.request.user
        form_kws["formtype"] = "create"
        return form_kws

    def form_valid(self, form):
        change_action_helper(form, self.request.user, create=True)
        return super(ActionCreateView, self).form_valid(form)

    def get_success_url(self, **kwargs):
        return self.object.get_absolute_url()

class ActionEditView(UserPassesTestMixin, generic.edit.UpdateView):
    model = Action
    form_class = ActionForm

    def test_func(self):
        obj = self.get_object()
        return obj.creator == self.request.user

    def get_form_kwargs(self):
        form_kws = super(ActionEditView, self).get_form_kwargs()
        form_kws["user"] = self.request.user
        form_kws["formtype"] = "update"
        return form_kws

    def form_valid(self, form):
        change_loc = True if self.get_object().location != self.object.location else False
        change_action_helper(form, self.request.user, create=False, change_loc=change_loc)
        return super(ActionEditView, self).form_valid(form)

class SlateRedirectView(generic.base.RedirectView):
    permanent = False
    query_string = True
    pattern_name = 'slate'
