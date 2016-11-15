from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.views import generic
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.core.exceptions import ObjectDoesNotExist

from django.contrib.auth.models import User
from profiles.models import Profile

def index(request):
    return HttpResponseRedirect(reverse('profiles'))

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

def toggle_relationships(request, username, toggle_type):
    current_profile = request.user.profile
    try:
        target_user = User.objects.get(username=username)
    except ObjectDoesNotExist: # If the target username got borked
        return HttpResponseRedirect(reverse('index'))

    relationship = current_profile.get_relationship_given_profile(target_user.profile)
    if not relationship:
        relationship = Relationship(person_A=current_profile, person_B=target_user.profile)

    if toggle_type == 'follow':
        status = relationship.toggle_following_for_current_profile(current_profile)
    elif toggle_type == 'account':
        status = relationship.toggle_accountability_for_current_profile(current_profile)
    elif toggle_type == 'mute':
        status = relationship.toggle_mute_for_current_profile(current_profile)

    return HttpResponseRedirect(reverse('profile', kwargs={'slug':target_user.username}))

# Add friend list view (or maybe wrap it into profile view?)
