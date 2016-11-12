from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.views import generic

from django.contrib.auth.models import User
from actions.models import Action

class IndexView(generic.ListView):
    template_name = "actions/actions.html"
    model = Action

class ActionView(generic.DetailView):
    template_name = 'actions/action.html'
    model = Action
