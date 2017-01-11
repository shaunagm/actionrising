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
from actions.models import Action, ActionTopic, ActionType
from actions.forms import ActionForm

@login_required
def index(request):
    return HttpResponseRedirect(reverse('actions'))

class ActionView(UserPassesTestMixin, generic.DetailView):
    template_name = 'actions/action.html'
    model = Action

    def get_context_data(self, **kwargs):
        context = super(ActionView, self).get_context_data(**kwargs)
        context['topic_or_type_list'] = self.object.get_tags()
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

def create_action_helper(object, types, topics, user):
    object.creator = user
    object.save()
    for atype in types:
        object.actiontypes.add(atype)
    for topic in topics:
        object.topics.add(topic)
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
        types = form.cleaned_data.pop('actiontypes')
        topics = form.cleaned_data.pop('topics')
        object = form.save(commit=False)
        self.object = create_action_helper(object, types, topics, self.request.user)
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
        object = form.save(commit=False)
        uf = []

        if self.get_object().location != self.object.location:
            uf = ['location']

        self.object = object.save(update_fields=uf)
        return super(ActionEditView, self).form_valid(form)

class TopicView(LoginRequiredMixin, generic.DetailView):
    template_name = 'actions/type_or_topic.html'
    model = ActionTopic

    def get_context_data(self, **kwargs):
        context = super(TopicView, self).get_context_data(**kwargs)
        context['action_list'] = filter_list_for_privacy(self.object.actions_for_topic.all(),
            self.request.user)
        return context

class TopicListView(LoginRequiredMixin, generic.ListView):
    template_name = "actions/topics.html"
    model = ActionTopic

class TypeView(LoginRequiredMixin, generic.DetailView):
    template_name = 'actions/type_or_topic.html'
    model = ActionType

    def get_context_data(self, **kwargs):
        context = super(TypeView, self).get_context_data(**kwargs)
        context['action_list'] = filter_list_for_privacy(self.object.actions_for_type.all(),
            self.request.user)
        return context

class TypeListView(LoginRequiredMixin, generic.ListView):
    template_name = "actions/types.html"
    model = ActionType
