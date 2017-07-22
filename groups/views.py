from django.views import generic
from django.contrib.auth.mixins import UserPassesTestMixin,  LoginRequiredMixin
from django.http import HttpResponseRedirect
from django.contrib.auth.models import Group

from mysite.lib.privacy import apply_check_privacy

from groups.models import GroupProfile


class GroupListView(generic.ListView):
    template_name = "groups/groups.html"
    model = GroupProfile

    def get_context_data(self, **kwargs):
        context = super(GroupListView, self).get_context_data(**kwargs)
        context['object_list'] = apply_check_privacy(self.get_queryset(), self.request.user)
        return context


class GroupView(generic.DetailView):
    template_name = "groups/group.html"
    model = GroupProfile
    slug_field = "groupname"


class GroupCreateView(LoginRequiredMixin, generic.edit.CreateView):
    model = GroupProfile
    template_name = "groups/group_form.html"
    fields = ['groupname', 'privacy', 'description', 'summary']

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.owner = self.request.user
        self.object.save()
        return HttpResponseRedirect(self.get_success_url())

    def get_success_url(self, **kwargs):
        return self.object.get_absolute_url()


class GroupEditView(UserPassesTestMixin, generic.edit.UpdateView):
    model = GroupProfile
    slug_field = "groupname"
    template_name = "groups/group_form.html"
    fields = ['privacy', 'description', 'summary']

    def test_func(self):
        obj = self.get_object()
        return obj.owner == self.request.user


class GroupAdminView(UserPassesTestMixin, generic.DetailView):
    emplate_name = "groups/admin_group.html"
    model = GroupProfile
    slug_field = "groupname"
