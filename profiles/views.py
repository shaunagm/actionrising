from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.views import generic
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.core.exceptions import ObjectDoesNotExist

from django.contrib.auth.models import User
from profiles.models import Profile, Relationship, ProfileActionRelationship
from actions.models import Action
from profiles.forms import ProfileActionRelationshipForm

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

def toggle_action_for_profile(request, slug, toggle_type):
    current_profile = request.user.profile
    try:
        action = Action.objects.get(slug=slug)
    except ObjectDoesNotExist: # If the target username got borked
        return HttpResponseRedirect(reverse('index'))

    if toggle_type == 'add':
        par, create = ProfileActionRelationship.objects.get_or_create(profile=current_profile, action=action)
        par.status = 'ace'
        par.save()

    if toggle_type == 'remove':
        par = ProfileActionRelationship.objects.get(profile=current_profile, action=action)
        par.delete()
    return HttpResponseRedirect(reverse('action', kwargs={'slug':action.slug}))

def manage_action(request, slug):
    par = ProfileActionRelationship.objects.get(action=Action.objects.get(slug=slug), profile=request.user.profile)
    if request.method == 'POST':
        form = ProfileActionRelationshipForm(request.POST)
        if form.is_valid():
            par.priority = form.cleaned_data['priority']
            par.status = form.cleaned_data['status']
            par.privacy = form.cleaned_data['privacy']
            par.save()
            for profile in form.cleaned_data['profiles']:
                # Right now this is pretty inefficient.  Would be nice to show users which of
                # their profile-buddies already had this action suggested to them.
                new_profile = User.objects.get(username=profile.user.username).profile
                new_par, created = ProfileActionRelationship.objects.get_or_create(profile=new_profile, action=par.action)
                if created:
                    new_par.status = 'sug'
                    new_par.save()
            return HttpResponseRedirect(reverse('action', kwargs={'slug':par.action.slug}))
        else:
            context = {'form': form}
            render(request, 'profiles/manage_action.html', context)
    else:
        form = ProfileActionRelationshipForm(par=par, initial={'privacy': par.privacy, 'priority': par.priority, 'status': par.status})
        context = {'form': form}
        return render(request, 'profiles/manage_action.html', context)

# Add friend list view (or maybe wrap it into profile view?)
