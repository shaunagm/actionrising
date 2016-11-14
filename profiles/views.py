from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.views import generic
from django.views.generic.edit import CreateView, UpdateView, DeleteView

from django.contrib.auth.models import User
from profiles.models import Profile

def index(request):
    return HttpResponseRedirect(reverse('profile', kwargs={'username':request.user.username}))

class ProfileView(generic.DetailView):
    template_name = 'profiles/profile.html'
    model = User
    slug_field = 'username'

class ProfileEditView(generic.UpdateView):
    model = Profile
    fields = ['verified', 'text', 'location', 'links']

    def get_success_url(self, **kwargs):
        return self.object.get_absolute_url()

class ProfileSearchView(generic.ListView):
    template_name = 'profiles/profiles.html'
    model = User

# Add friend list view (or maybe wrap it into profile view?)
