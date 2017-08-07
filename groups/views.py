from django.views import generic
from django.contrib.auth.mixins import UserPassesTestMixin,  LoginRequiredMixin
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.contrib.auth.models import Group, User
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse

from mysite.lib.privacy import apply_check_privacy, check_privacy

from groups.models import GroupProfile, PendingMember
from groups.forms import GroupForm
from groups.lib.utils import get_potential_invitees


def index(request):
    return HttpResponseRedirect(reverse('groups'))


class GroupListView(generic.ListView):
    template_name = "groups/groups.html"
    model = GroupProfile


class GroupView(UserPassesTestMixin, generic.DetailView):
    template_name = "groups/group.html"
    model = Group
    slug_field = "name"

    def get_object(self, queryset=None):
        # We want groupprofile, but the url-safe slug is auth group name.
        auth_group = super(GroupView, self).get_object()
        return auth_group.groupprofile

    def get_context_data(self, **kwargs):
        context = super(GroupView, self).get_context_data(**kwargs)
        context['can_access'] = check_privacy(self.object, self.request.user)
        context['is_member'] = self.object.hasMember(self.request.user)
        context['is_admin'] = self.object.hasAdmin(self.request.user)
        context['is_owner'] = self.object.owner == self.request.user
        context['tag_list'] = self.object.tags.all()
        # There's a small chance that an invite & request will both be active at once.
        context['pending_request'] = PendingMember.objects.filter(group=self.object,
            user=self.request.user, status="request").first()
        context['pending_invite'] = PendingMember.objects.filter(group=self.object,
            user=self.request.user, status="invite").first()
        return context

    def test_func(self):
        obj = self.get_object()
        return check_privacy(obj, self.request.user)


class GroupCreateView(LoginRequiredMixin, generic.edit.CreateView):
    model = GroupProfile
    template_name = "groups/group_form.html"
    form_class = GroupForm

    def get_form_kwargs(self):
        form_kws = super(GroupCreateView, self).get_form_kwargs()
        form_kws["user"] = self.request.user
        return form_kws

    def get_success_url(self, **kwargs):
        return self.object.get_absolute_url()


class GroupEditView(UserPassesTestMixin, generic.edit.UpdateView):
    model = Group
    slug_field = "name"
    template_name = "groups/group_form.html"
    form_class = GroupForm

    def get_object(self, queryset=None):
        # We want groupprofile, but the url-safe slug is auth group name.
        auth_group = super(GroupEditView, self).get_object()
        return auth_group.groupprofile

    def test_func(self):
        obj = self.get_object()
        return obj.owner == self.request.user


class GroupAdminView(UserPassesTestMixin, generic.DetailView):
    template_name = "groups/admin_group.html"
    model = Group
    slug_field = "name"

    def get_object(self, queryset=None):
        # We want groupprofile, but the url-safe slug is auth group name.
        auth_group = super(GroupAdminView, self).get_object()
        return auth_group.groupprofile

    def get_context_data(self, **kwargs):
        context = super(GroupAdminView, self).get_context_data(**kwargs)
        context['requests'] = PendingMember.objects.filter(group=self.object, status="request")
        context['invites'] = PendingMember.objects.filter(group=self.object, status="invite")
        context['friends'] = get_potential_invitees(self.object, self.request.user)
        return context

    def test_func(self):
        obj = self.get_object()
        return obj.hasAdmin(self.request.user)


@login_required
def join_group(request):
    group_pk = request.GET.get('group_pk', None)
    groupprofile = GroupProfile.objects.get(pk=group_pk)
    if groupprofile.hasMember(request.user):
        return JsonResponse({'message': 'You are already a member of this group'})
    if groupprofile.membership == "open":
        groupprofile.addMember(request.user)
        return JsonResponse({'message': 'You have joined this group.'})
    return JsonResponse({'message': 'There was an error joining this group.'})


@login_required
def leave_group(request):
    group_pk = request.GET.get('group_pk', None)
    groupprofile = GroupProfile.objects.get(pk=group_pk)
    if groupprofile.owner == request.user:
        return JsonResponse({'message':
            'You cannot leave this group because you are the owner.'})
    else:
        groupprofile.removeMember(request.user)
        return JsonResponse({'message': 'You have left this group.'})


@login_required
def remove_from_group(request):
    group_pk = request.GET.get('group_pk', None)
    groupprofile = GroupProfile.objects.get(pk=group_pk)
    user_pk = request.GET.get('user_pk', None)
    if str(request.user.pk) == user_pk:
        return JsonResponse({'message':
            'You cannot remove yourself from the group.'})
    removed_user = User.objects.get(pk=user_pk)
    if groupprofile.hasAdmin(removed_user) and request.user != groupprofile.owner:
        return JsonResponse({'message':
            'You do not have permission to remove admins.'})
    groupprofile.removeMember(removed_user)
    return JsonResponse({'message': 'User has been removed from group.'})


@login_required
def request_to_join_group(request):
    # Note that request to join should only be called by groups set to request
    # membership status, as oppposed to invites, which can be used for all groups.
    group_pk = request.GET.get('group_pk', None)
    groupprofile = GroupProfile.objects.get(pk=group_pk)
    if groupprofile.hasMember(request.user):
        return JsonResponse({'message': 'You are already a member of this group'})
    if groupprofile.membership != "request":
        return JsonResponse({'message':
            'There was an error processing your request to join this group.'})
    PendingMember.objects.get_or_create(group=groupprofile, user=request.user,
        status="request")
    return JsonResponse({'message': 'You have requested to join this group.'})


@login_required
def approve_request_to_join_group(request):
    group_pk = request.GET.get('group_pk', None)
    groupprofile = GroupProfile.objects.get(pk=group_pk)
    pending_pk = request.GET.get('pending_pk', None)
    pending = PendingMember.objects.get(pk=pending_pk)
    approved = request.GET.get('approved', None)
    if approved == "yes":
        groupprofile.addMember(pending.user)
        pending.delete()
        return JsonResponse({'message': 'Request approved.'})
    elif approved == "no":
        pending.delete()
        return JsonResponse({'message': 'Request denied.'})
    return JsonResponse({'message': 'There was an error processing the request.'})


@login_required
def invite_to_group(request):
    group_pk = request.GET.get('group_pk', None)
    groupprofile = GroupProfile.objects.get(pk=group_pk)
    usernames = request.GET.getlist('usernames[]')
    invitees = []
    for user in usernames:
        invited_user = User.objects.get(username=user)
        if groupprofile.hasMember(invited_user):
            continue
        pending, created = PendingMember.objects.get_or_create(group=groupprofile,
            user=invited_user, inviter=request.user, status="invite")
        if created:
            invitees.append(invited_user)
    invitee_string = 'You have invited ' + ' '.join([user.username for user in invitees])
    return JsonResponse({'message': invitee_string})


@login_required
def approve_invite_to_group(request):
    group_pk = request.GET.get('group_pk', None)
    groupprofile = GroupProfile.objects.get(pk=group_pk)
    pending_pk = request.GET.get('pending_pk', None)
    pending = PendingMember.objects.get(pk=pending_pk)
    approved = request.GET.get('approved', None)
    if approved == "yes":
        groupprofile.addMember(request.user)
        pending.delete()
        return JsonResponse({'message': 'You have joined the group.'})
    if approved == "no":
        pending.delete()
        return JsonResponse({'message': 'You have declined to join the group.'})
    return JsonResponse({'message':
        'There was an error processing your invite to join this group.'})


@login_required
def change_admin(request):
    group_pk = request.GET.get('group_pk', None)
    groupprofile = GroupProfile.objects.get(pk=group_pk)
    if request.user != groupprofile.owner:
        return JsonResponse({'message':
            'You do not have permission to add or remove admins.'})
    user_pk = request.GET.get('user_pk', None)
    user_to_change = User.objects.get(pk=user_pk)
    action = request.GET.get('action', None)
    if action == "add":
        groupprofile.addAdmin(user_to_change)
        return JsonResponse({'message': 'User added as admin.'})
    if action == "remove":
        groupprofile.removeAdmin(user_to_change)
        return JsonResponse({'message': 'User removed as admin.'})
    return JsonResponse({'message':
        'There was a problem changing the admin status of the user.'})