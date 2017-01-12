from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.views import generic
from django.contrib.auth.mixins import UserPassesTestMixin,  LoginRequiredMixin
from django.contrib.auth.decorators import login_required

from mysite.lib.privacy import filter_list_for_privacy
from tags.models import Tag

class TagView(LoginRequiredMixin, generic.DetailView):
    template_name = 'tags/tag.html'
    model = Tag

    def get_context_data(self, **kwargs):
        context = super(TagView, self).get_context_data(**kwargs)
        context['action_list'] = filter_list_for_privacy(self.object.actions.all(),
            self.request.user)
        context['slate_list'] = filter_list_for_privacy(self.object.actions.all(),
            self.request.user)
        context['profile_list'] = filter_list_for_privacy(self.object.actions.all(),
            self.request.user)
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
