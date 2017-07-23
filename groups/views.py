from django.views import generic
from django.contrib.auth.mixins import UserPassesTestMixin,  LoginRequiredMixin
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse

from mysite.lib.privacy import apply_check_privacy, check_privacy

from groups.models import GroupProfile
from groups.forms import GroupForm


def index(request):
    return HttpResponseRedirect(reverse('groups'))


class GroupListView(generic.ListView):
    template_name = "groups/groups.html"
    model = GroupProfile


class GroupView(UserPassesTestMixin, generic.DetailView):
    template_name = "groups/group.html"
    model = GroupProfile
    slug_field = "groupname"

    def get_context_data(self, **kwargs):
        context = super(GroupView, self).get_context_data(**kwargs)
        context['can_access'] = check_privacy(self.object, self.request.user)
        context['is_member'] = self.object.hasMember(self.request.user)
        context['is_admin'] = self.object.hasAdmin(self.request.user)
        context['is_owner'] = self.object.owner == self.request.user
        context['tag_list'] = self.object.tags.all()
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
    model = GroupProfile
    slug_field = "groupname"
    template_name = "groups/group_form.html"
    form_class = GroupForm

    def test_func(self):
        obj = self.get_object()
        return obj.owner == self.request.user


class GroupAdminView(UserPassesTestMixin, generic.DetailView):
    template_name = "groups/admin_group.html"
    model = GroupProfile
    slug_field = "groupname"

    def test_func(self):
        obj = self.get_object()
        return obj.hasAdmin(self.request.user)
