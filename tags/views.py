from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.views import generic
from django.contrib.auth.mixins import UserPassesTestMixin,  LoginRequiredMixin
from django.contrib.auth.decorators import login_required

from mysite.lib.privacy import filtered_list_view
from tags.models import Tag
from actions.models import Action
from slates.models import Slate
from profiles.models import Profile

class TagView(LoginRequiredMixin, generic.DetailView):
    template_name = 'tags/tag.html'
    model = Tag

    def get_context_data(self, **kwargs):
        context = super(TagView, self).get_context_data(**kwargs)
        context['action_list'] = filtered_list_view(Action, self.request.user)
        context['slate_list'] = filtered_list_view(Slate, self.request.user)
        context['profile_list'] = filtered_list_view(Profile, self.request.user)
        return context

class TagListView(LoginRequiredMixin, generic.ListView):
    template_name = "tags/tags.html"
    model = Tag

    def get_context_data(self, **kwargs):
        context = super(TagListView, self).get_context_data(**kwargs)
        if 'kind' in self.kwargs:
            tags = Tag.objects.filter(kind=self.kwargs['kind'])
            if tags:
                context['object_list'] = tags
                context['tag_filter'] = self.kwargs['kind']
        return context
