from itertools import chain

from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.views import generic
from django.contrib.auth.mixins import UserPassesTestMixin,  LoginRequiredMixin
from django.contrib.auth.decorators import login_required

from mysite.utils import check_privacy

from django.contrib.auth.models import User
from actions.models import Action, ActionTopic, ActionType, Slate, SlateActionRelationship

@login_required
def index(request):
    return HttpResponseRedirect(reverse('actions'))

class ActionView(UserPassesTestMixin, generic.DetailView):
    template_name = 'actions/action.html'
    model = Action

    def get_context_data(self, **kwargs):
        context = super(ActionView, self).get_context_data(**kwargs)
        topic_list = self.object.topics.all()
        type_list = self.object.actiontypes.all()
        context['topic_or_type_list'] = list(chain(topic_list, type_list))
        return context

    def test_func(self):
        obj = self.get_object()
        return check_privacy(obj, self.request.user)

class ActionListView(LoginRequiredMixin, generic.ListView):
    template_name = "actions/actions.html"
    model = Action

class ActionCreateView(LoginRequiredMixin, generic.edit.CreateView):
    model = Action
    fields = ['slug', 'title', 'anonymize', 'main_link', 'text', 'privacy', 'location', 'status', 'has_deadline', 'deadline', 'topics', 'actiontypes']

    def form_valid(self, form):
        types = form.cleaned_data.pop('actiontypes')
        topics = form.cleaned_data.pop('topics')
        self.object = form.save(commit=False)
        self.object.creator = self.request.user
        self.object.save()
        for atype in types:
            self.object.actiontypes.add(atype)
        for topic in topics:
            self.object.topics.add(topic)
        return super(ActionCreateView, self).form_valid(form)

    def get_success_url(self, **kwargs):
        return self.object.get_absolute_url()

class ActionEditView(UserPassesTestMixin, generic.edit.UpdateView):
    model = Action
    fields = ['slug', 'title', 'anonymize', 'main_link', 'text', 'privacy', 'location', 'status', 'has_deadline', 'deadline', 'topics', 'actiontypes']

    def test_func(self):
        obj = self.get_object()
        return obj.creator == self.request.user

class TopicView(LoginRequiredMixin, generic.DetailView):
    template_name = 'actions/type_or_topic.html'
    model = ActionTopic

    def get_context_data(self, **kwargs):
        context = super(TopicView, self).get_context_data(**kwargs)
        context['action_list'] = self.object.actions_for_topic.all()
        return context

class TopicListView(LoginRequiredMixin, generic.ListView):
    template_name = "actions/topics.html"
    model = ActionTopic

class TypeListView(LoginRequiredMixin, generic.ListView):
    # Note: templates can likely be refactored to use same template as TopicListView
    template_name = "actions/types.html"
    model = ActionType

class TypeView(LoginRequiredMixin, generic.DetailView):
    template_name = 'actions/type_or_topic.html'
    model = ActionType

    def get_context_data(self, **kwargs):
        context = super(TypeView, self).get_context_data(**kwargs)
        context['action_list'] = self.object.actions_for_type.all()
        return context

class SlateView(UserPassesTestMixin, generic.DetailView):
    template_name = 'actions/slate.html'
    model = Slate

    def test_func(self):
        obj = self.get_object()
        return check_privacy(obj, self.request.user)

class SlateListView(LoginRequiredMixin, generic.ListView):
    # Note: templates can likely be refactored to use same template as TopicListView
    template_name = "actions/slates.html"
    model = Slate

class SlateCreateView(LoginRequiredMixin, generic.edit.CreateView):
    model = Slate
    fields = ['slug', 'title', 'text', 'status', 'privacy', 'actions']

    def form_valid(self, form):
        actions = form.cleaned_data.pop('actions')
        self.object = form.save(commit=False)
        self.object.creator = self.request.user
        self.object.save()
        for action in actions:
            SlateActionRelationship.objects.create(slate=self.object, action=action)
        return super(SlateCreateView, self).form_valid(form)

    def get_success_url(self, **kwargs):
        return self.object.get_absolute_url()

class SlateEditView(UserPassesTestMixin, generic.edit.UpdateView):
    model = Slate
    fields = ['slug', 'title', 'text', 'status', 'privacy', 'actions']

    def form_valid(self, form):
        actions = form.cleaned_data.pop('actions')
        self.object = form.save(commit=False)
        self.object.creator = self.request.user
        self.object.save()
        for action in actions:
            if action not in self.object.actions.all():
                SlateActionRelationship.objects.create(slate=self.object, action=action)
        for action in self.object.actions.all():
            if action not in actions:
                sar = SlateActionRelationship.objects.get(slate=self.object, action=action)
                sar.delete()
        return super(SlateEditView, self).form_valid(form)

    def get_success_url(self, **kwargs):
        return self.object.get_absolute_url()

    def test_func(self):
        obj = self.get_object()
        return obj.creator == self.request.user
