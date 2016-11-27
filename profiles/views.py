from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.views import generic
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.mixins import UserPassesTestMixin,  LoginRequiredMixin
from django.contrib.auth.decorators import login_required

from mysite.utils import check_privacy

from django.contrib.auth.models import User
from profiles.models import Profile, Relationship, ProfileActionRelationship
from actions.models import Action, Slate, SlateActionRelationship
from profiles.forms import ProfileForm, ProfileActionRelationshipForm

@login_required
def index(request):
    return HttpResponseRedirect(reverse('profiles'))

class ProfileView(UserPassesTestMixin, generic.DetailView):
    template_name = 'profiles/profile.html'
    model = User
    slug_field = 'username'

    def test_func(self):
        obj = self.get_object()
        return check_privacy(obj.profile, self.request.user)

    def get_context_data(self, **kwargs):
        context = super(ProfileView, self).get_context_data(**kwargs)
        context['created_actions'] = self.object.profile.get_most_recent_actions_created(self.request.user)
        context['tracked_actions'] = self.object.profile.get_most_recent_actions_tracked(self.request.user)
        return context

class ProfileEditView(UserPassesTestMixin, generic.UpdateView):
    model = Profile
    form_class = ProfileForm

    def test_func(self):
        obj = self.get_object()
        return obj.user == self.request.user

    def get_success_url(self, **kwargs):
        return self.object.get_absolute_url()

class ProfileToDoView(UserPassesTestMixin, generic.DetailView):
    template_name = 'profiles/todo.html'
    model = User
    slug_field = 'username'

    def test_func(self):
        obj = self.get_object()
        return obj == self.request.user  # No access unless this is you

    def get_context_data(self, **kwargs):
        context = super(ProfileToDoView, self).get_context_data(**kwargs)
        context['has_notes'] = True
        context['can_edit_actions'] = True
        context['actions'] = self.object.profile.get_open_pars(self.request.user)
        context['suggested_actions'] = self.object.profile.get_suggested_actions_count()
        return context

class ProfileSuggestedView(UserPassesTestMixin, generic.DetailView):
    template_name = 'profiles/suggested.html'
    model = User
    slug_field = 'username'

    def test_func(self):
        obj = self.get_object()
        return obj == self.request.user  # No access unless this is you

    def get_context_data(self, **kwargs):
        context = super(ProfileSuggestedView, self).get_context_data(**kwargs)
        context['actions'] = self.object.profile.get_suggested_actions()
        return context

class ProfileSearchView(LoginRequiredMixin, generic.ListView):
    template_name = 'profiles/profiles.html'
    model = User

def toggle_relationships_helper(toggle_type, current_profile, target_profile):
    relationship = current_profile.get_relationship_given_profile(target_profile)
    if not relationship:
        relationship = Relationship(person_A=current_profile, person_B=target_profile)
    if toggle_type == 'follow':
        return relationship.toggle_following_for_current_profile(current_profile)
    elif toggle_type == 'account':
        return relationship.toggle_accountability_for_current_profile(current_profile)
    elif toggle_type == 'mute':
        return relationship.toggle_mute_for_current_profile(current_profile)

@login_required
def toggle_relationships(request, username, toggle_type):
    current_profile = request.user.profile
    try:
        target_user = User.objects.get(username=username)
    except ObjectDoesNotExist: # If the target username got borked
        return HttpResponseRedirect(reverse('index'))
    status = toggle_relationships_helper(toggle_type, current_profile, target_user.profile)
    return HttpResponseRedirect(reverse('profile', kwargs={'slug':target_user.username}))

def toggle_par_helper(toggle_type, current_profile, action):
    if toggle_type == 'add':
        par, create = ProfileActionRelationship.objects.get_or_create(profile=current_profile, action=action)
        par.status = 'ace'
        par.save()
    if toggle_type == 'remove':
        par = ProfileActionRelationship.objects.get(profile=current_profile, action=action)
        par.delete()

@login_required
def toggle_action_for_profile(request, slug, toggle_type):
    current_profile = request.user.profile
    try:
        action = Action.objects.get(slug=slug)
    except ObjectDoesNotExist: # If the action slug got borked
        return HttpResponseRedirect(reverse('index'))
    toggle_par_helper(toggle_type, current_profile, action)
    return HttpResponseRedirect(reverse('action', kwargs={'slug':action.slug}))

def manage_action_helper(par, form, user):
    par.priority = form.cleaned_data['priority']
    par.status = form.cleaned_data['status']
    par.privacy = form.cleaned_data['privacy']
    par.notes = form.cleaned_data['notes']
    par.save()
    for profile in form.cleaned_data['profiles']:
        # TODO: Right now this is pretty inefficient.  Would be nice to show users which of
        # their profile-buddies already had this action suggested to them.
        new_profile = User.objects.get(username=profile.user.username).profile
        new_par, created = ProfileActionRelationship.objects.get_or_create(profile=new_profile, action=par.action)
        new_par.status = 'sug'
        new_par.save()
        new_par.add_suggester(user.username)
    for slate in form.cleaned_data['slates']:
        # TODO: Right now this is pretty inefficient.  Would be nice to show users which of
        # their slates already had this action added to them.
        new_slate = Slate.objects.get(slug=slate)
        new_sar, created = SlateActionRelationship.objects.get_or_create(slate=new_slate, action=par.action)

@login_required
def manage_action(request, slug):
    par = ProfileActionRelationship.objects.get(action=Action.objects.get(slug=slug), profile=request.user.profile)
    if request.method == 'POST':
        form = ProfileActionRelationshipForm(request.POST)
        if form.is_valid():
            manage_action_helper(par, form, request.user)
            return HttpResponseRedirect(reverse('action', kwargs={'slug':par.action.slug}))
        else:
            context = {'form': form}
            render(request, 'profiles/manage_action.html', context)
    else:
        form = ProfileActionRelationshipForm(par=par, initial={'privacy': par.privacy, 'priority': par.priority, 'status': par.status})
        context = {'form': form}
        return render(request, 'profiles/manage_action.html', context)

def mark_as_done_helper(profile, action, mark_as):
    par = ProfileActionRelationship.objects.filter(profile=profile, action=action).first()
    if mark_as == 'done':
        par.status = 'don'
    else:
        par.status = 'ace'
    par.save()
    return par

@login_required
def mark_as_done(request, slug, mark_as):
    current_profile = request.user.profile
    try:
        action = Action.objects.get(slug=slug)
    except ObjectDoesNotExist: # If the action slug got borked
        return HttpResponseRedirect(reverse('index'))
    mark_as_done_helper(current_profile, action, mark_as)
    return HttpResponseRedirect(reverse('action', kwargs={'slug':action.slug}))

def manage_suggested_action_helper(par, type):
    if type == 'accept':
        par.status = "ace"
    if type == 'reject':
        par.status = "wit"
    par.save()
    return par

@login_required
def manage_suggested_action(request, slug, type):
    current_profile = request.user.profile
    try:
        action = Action.objects.get(slug=slug)
        par = ProfileActionRelationship.objects.get(action=action, profile=current_profile)
    except ObjectDoesNotExist: # If the action slug got borked
        return HttpResponseRedirect(reverse('index'))
    manage_suggested_action_helper(par, type)
    return HttpResponseRedirect(reverse('suggested', kwargs={'slug':request.user}))
