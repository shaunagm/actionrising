import datetime, pytz

from django.shortcuts import render
from django.http import HttpResponseRedirect, Http404
from django.core.urlresolvers import reverse
from django.views import generic
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.mixins import UserPassesTestMixin, LoginRequiredMixin
from django.contrib.auth.decorators import login_required

from actstream.actions import follow, unfollow
from mysite.lib.privacy import check_privacy, filter_list_for_privacy, filter_list_for_privacy_annotated
from mysite.lib.choices import PrivacyChoices, ToDoStatusChoices
from django.contrib.auth.models import User
from profiles.models import (Profile, Relationship, ProfileActionRelationship,
    ProfileSlateRelationship)
from actions.models import Action
from slates.models import Slate, SlateActionRelationship
from profiles.forms import ProfileForm, ProfileActionRelationshipForm

@login_required
def index(request):
    return HttpResponseRedirect(reverse('profiles'))

class ProfileView(UserPassesTestMixin, generic.DetailView):
    template_name = 'profiles/profile.html'
    slug_field = 'username'
    model = User

    def test_func(self):
        obj = self.get_object()
        return check_privacy(obj.profile, self.request.user)

    def get_context_data(self, **kwargs):
        context = super(ProfileView, self).get_context_data(**kwargs)
        if self.request.user.is_authenticated():
            context['created_actions'] = filter_list_for_privacy_annotated(
                self.object.profile.get_most_recent_actions_created(), self.request.user)
            context['tracked_actions'] = filter_list_for_privacy_annotated(
                self.object.profile.get_most_recent_actions_tracked(), self.request.user)
            obj = self.get_object()
            context['total_actions'] = obj.profile.profileactionrelationship_set.count()
            context['percent_finished'] = obj.profile.get_percent_finished()
            context['action_streak_current'] = obj.profile.get_action_streak()
            current_profile = self.request.user.profile
            relationship = current_profile.get_relationship_given_profile(obj.profile)
            if relationship:
                context['follows'] = relationship.current_profile_follows_target(current_profile)
                context['mutes'] = relationship.current_profile_mutes_target(current_profile)
                context['notified_of'] = relationship.current_profile_notified_of_target(current_profile)
        return context

class ProfileEditView(UserPassesTestMixin, generic.UpdateView):
    model = Profile
    form_class = ProfileForm
    slug_field = 'user'

    def get_object(self, queryset=None):
        slug = self.kwargs.get(self.slug_url_kwarg, None)
        if slug:
            user = User.objects.get(username=slug)
            return Profile.objects.get(user=user)
        else:
            raise Http404(_(u"No user supplied to profile edit view"))

    def test_func(self):
        obj = self.get_object()
        return obj.user == self.request.user

    def get_form_kwargs(self):
        form_kws = super(ProfileEditView, self).get_form_kwargs()
        form_kws["user"] = self.request.user
        return form_kws

    def get_success_url(self, **kwargs):
        return self.object.get_absolute_url()

class ToDoView(LoginRequiredMixin, generic.TemplateView):
    template_name = 'profiles/todo.html'

    def get_context_data(self, **kwargs):
        context = super(ToDoView, self).get_context_data(**kwargs)
        context['has_notes'] = True
        context['can_edit_actions'] = True
        context['use_status'] = False
        context['actions'] = self.request.user.profile.get_open_pars()
        context['suggested_actions'] = self.request.user.profile.get_suggested_actions_count()
        return context

class ProfileSuggestedView(UserPassesTestMixin, generic.DetailView):
    template_name = 'profiles/suggested.html'
    slug_field = 'username'
    model = User

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

    def get_context_data(self, **kwargs):
        context = super(ProfileSearchView, self).get_context_data(**kwargs)
        context['object_list'] = [profile.user for profile in Profile.objects.filter(current_privacy__in=[PrivacyChoices.public, PrivacyChoices.sitewide])]
        return context

class FeedView(LoginRequiredMixin, generic.TemplateView):
    template_name = 'profiles/feed.html'

class ActivityView(LoginRequiredMixin, generic.TemplateView):
    template_name = 'profiles/activity.html'

def toggle_relationships_helper(toggle_type, current_profile, target_profile):
    relationship = current_profile.get_relationship_given_profile(target_profile)
    if not relationship:
        relationship = Relationship.objects.create(person_A=current_profile, person_B=target_profile)
    if toggle_type == 'follow':
        return relationship.toggle_following_for_current_profile(current_profile)
    elif toggle_type == 'account':
        return relationship.toggle_accountability_for_current_profile(current_profile)
    elif toggle_type == 'mute':
        return relationship.toggle_mute_for_current_profile(current_profile)
    elif toggle_type == 'notify':
        return relationship.toggle_notified_of_for_current_profile(current_profile)

@login_required
def toggle_relationships(request, slug, toggle_type):
    current_profile = request.user.profile
    try:
        target_user = User.objects.get(username=slug)
    except ObjectDoesNotExist: # If the target username got borked
        return HttpResponseRedirect(reverse('index'))
    status = toggle_relationships_helper(toggle_type, current_profile, target_user.profile)
    return HttpResponseRedirect(reverse('profile', kwargs={'slug':target_user.username}))

def toggle_par_helper(toggle_type, current_profile, action):
    if toggle_type == 'add':
        par, create = ProfileActionRelationship.objects.get_or_create(profile=current_profile, action=action)
        par.status = ToDoStatusChoices.accepted
        par.date_accepted = datetime.datetime.now(tz=pytz.utc)
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

def toggle_psr_helper(toggle_type, current_profile, slate):
    psr, create = ProfileSlateRelationship.objects.get_or_create(profile=current_profile,
        slate=slate)
    if toggle_type == 'add':
        psr.save()
        follow(current_profile.user, slate, actor_only=False)
        return
    if toggle_type == 'remove':
        psr.delete()
        unfollow(current_profile.user, slate)
        return
    if toggle_type == 'notify':
        psr.notify_of_additions = True
        psr.save()
        return
    if toggle_type == 'stop_notify':
        psr.notify_of_additions = False
        psr.save()

@login_required
def toggle_slate_for_profile(request, slug, toggle_type):
    current_profile = request.user.profile
    try:
        slate = Slate.objects.get(slug=slug)
    except ObjectDoesNotExist: # If the action slug got borked
        return HttpResponseRedirect(reverse('index'))
    toggle_psr_helper(toggle_type, current_profile, slate)
    return HttpResponseRedirect(reverse('slate', kwargs={'slug':slate.slug}))

def manage_action_helper(par, form, user):
    par.priority = form.cleaned_data['priority']
    par.status = form.cleaned_data['status']
    par.notes = form.cleaned_data['notes']
    par.save()
    for profile in form.cleaned_data['profiles']:
        # TODO: Right now this is pretty inefficient.  Would be nice to show users which of
        # their profile-buddies already had this action suggested to them.
        new_profile = User.objects.get(username=profile.user.username).profile
        new_par, created = ProfileActionRelationship.objects.get_or_create(
            profile=new_profile, action=par.action,
            defaults={'status': ToDoStatusChoices.suggested, 'last_suggester': user })
        new_par.add_suggester(user.username)
    for slate in form.cleaned_data['slates']:
        # TODO: Right now this is pretty inefficient.  Would be nice to show users which of
        # their slates already had this action added to them.
        new_slate = Slate.objects.get(slug=slate.slug)
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
        form = ProfileActionRelationshipForm(par=par, initial={'priority': par.priority, 'status': par.status, 'notes': par.notes })
        context = {'form': form}
        return render(request, 'profiles/manage_action.html', context)

def mark_as_done_helper(profile, action, mark_as):
    par, created = ProfileActionRelationship.objects.get_or_create(profile=profile,
        action=action)
    if mark_as == 'done':
        par.status = ToDoStatusChoices.done
        par.date_finished = datetime.datetime.now(tz=pytz.utc)
    else:
        par.status = ToDoStatusChoices.accepted
        par.date_accepted = datetime.datetime.now(tz=pytz.utc)
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
        par.status = ToDoStatusChoices.accepted
        par.date_accepted = datetime.datetime.now(tz=pytz.utc)
    if type == 'reject':
        par.status = ToDoStatusChoices.rejected
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
    return HttpResponseRedirect(reverse('suggested', kwargs={'pk':request.user.pk}))

class DashboardView(LoginRequiredMixin, generic.TemplateView):
    template_name = "profiles/dashboard.html"

    def get_context_data(self, **kwargs):
        context = super(DashboardView, self).get_context_data(**kwargs)
        context['open_actions'] = self.request.user.profile.get_open_pars()
        context['your_filters'] = self.request.user.actionfilter_set.all()
        context['your_friends'] = self.request.user.profile.get_list_of_relationships()
        context['followed_slates'] = self.request.user.profile.profileslaterelationship_set.all()
        context['created_actions'] =  self.request.user.action_set.all()
        context['created_slates'] = self.request.user.slate_set.all()
        context['suggested_pars'] = self.request.user.profile.get_suggested_actions()
        # If none of the above is filled out, include alert.
        if not (context['open_actions'] or context['your_friends'] or
            context['your_filters'] or context['followed_slates'] or
            context['created_actions'] or context['created_slates']):
            context['new_user'] = True
        return context
