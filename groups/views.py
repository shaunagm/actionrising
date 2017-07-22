from django.views import generic
from django.contrib.auth.mixins import UserPassesTestMixin,  LoginRequiredMixin

from groups.models import GroupProfile


class GroupListView(generic.ListView):
    template_name = "groups/groups.html"
    model = GroupProfile


class GroupView(UserPassesTestMixin, generic.DetailView):
    template_name = "groups/group.html"
    model = GroupProfile
    slug_field = "groupname"


class GroupCreateView(LoginRequiredMixin, generic.edit.CreateView):
    model = GroupProfile
    template_name = "groups/create_group.html"


class GroupEditView(UserPassesTestMixin, generic.edit.UpdateView):
    model = GroupProfile
    slug_field = "groupname"
    template_name = "groups/edit_group.html"


class GroupAdminView(UserPassesTestMixin, generic.DetailView):
    emplate_name = "groups/admin_group.html"
    model = GroupProfile
    slug_field = "groupname"
