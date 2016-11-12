from itertools import chain

from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.views import generic

from django.contrib.auth.models import User
from actions.models import Action, ActionTopic, ActionType

class IndexView(generic.ListView):
    template_name = "actions/actions.html"
    model = Action

class ActionCreateView(generic.edit.CreateView):
    model = Action
    fields = ['slug', 'title', 'anonymize', 'main_link', 'text', 'privacy', 'location', 'status', 'has_deadline', 'deadline']

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.creator = self.request.user
        self.object.save()
        return super(ActionCreateView, self).form_valid(form)

    def get_success_url(self, **kwargs):
        return self.object.get_absolute_url() 

class ActionEditView(generic.edit.UpdateView):
    model = Action
    fields = ['slug', 'title', 'anonymize', 'main_link', 'text', 'privacy', 'location', 'status', 'has_deadline', 'deadline']

class ActionView(generic.DetailView):
    template_name = 'actions/action.html'
    model = Action

    def get_context_data(self, **kwargs):
        context = super(ActionView, self).get_context_data(**kwargs)
        topic_list = self.object.topics.all()
        type_list = self.object.actiontypes.all()
        context['topic_or_type_list'] = list(chain(topic_list, type_list))
        return context

class TopicListView(generic.ListView):
    template_name = "actions/topics.html"
    model = ActionTopic

class TopicView(generic.DetailView):
    template_name = 'actions/type_or_topic.html'
    model = ActionTopic

    def get_context_data(self, **kwargs):
        context = super(TopicView, self).get_context_data(**kwargs)
        context['action_list'] = self.object.actions.all()
        return context

class TypeListView(generic.ListView):
    # Note: templates can likely be refactored to use same template as TopicListView
    template_name = "actions/types.html"
    model = ActionType

class TypeView(generic.DetailView):
    template_name = 'actions/type_or_topic.html'
    model = ActionType

    def get_context_data(self, **kwargs):
        context = super(TypeView, self).get_context_data(**kwargs)
        context['action_list'] = self.object.actions.all()
        return context
