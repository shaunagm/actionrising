from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.views import generic
from django.contrib.auth.mixins import UserPassesTestMixin,  LoginRequiredMixin
from django.contrib.auth.decorators import login_required

from flags.lib.flag_helpers import get_user_flag_if_exists
from mysite.lib.choices import PrivacyChoices, StatusChoices
from mysite.lib.privacy import (check_privacy, filter_list_for_privacy,
    filter_list_for_privacy_annotated)
from misc.models import RecommendationTracker
from profiles.lib.trackers import get_tracker_data_for_slate
from slates.models import Slate, SlateActionRelationship
from slates.forms import SlateForm, SlateActionRelationshipForm

class SlateView(UserPassesTestMixin, generic.DetailView):
    template_name = 'slates/slate.html'
    model = Slate

    def get_context_data(self, **kwargs):
        context = super(SlateView, self).get_context_data(**kwargs)
        context['has_notes'] = True
        context['can_edit_actions'] = True if self.object.creator == self.request.user else False
        context['is_slate'] = True
        context['flag'] = get_user_flag_if_exists(self.object, self.request.user)
        annotated_list = filter_list_for_privacy_annotated(self.object.slateactionrelationship_set.all(),
            self.request.user)
        context['actions'] = annotated_list['public_list']
        context['hidden_actions'] = annotated_list['anonymous_count']
        if self.request.user.is_authenticated():
            context['psr'] = self.request.user.profile.get_psr_given_slate(self.object)
        context['tracker_data'] = get_tracker_data_for_slate(self.object, self.request.user)
        context['tag_list'] = self.object.tags.all()
        return context

    def test_func(self):
        obj = self.get_object()
        return check_privacy(obj, self.request.user)

class SlateListView(LoginRequiredMixin, generic.ListView):
    # Note: templates can likely be refactored to use same template as TopicListView
    template_name = "slates/slates.html"
    model = Slate
    queryset = Slate.objects.filter(status__in=[StatusChoices.ready, StatusChoices.finished]).filter(current_privacy__in=[PrivacyChoices.public, PrivacyChoices.sitewide])

class PublicSlateListView(generic.ListView):
    template_name = "slates/slates.html"
    model = Slate
    queryset = Slate.objects.filter(status__in=[StatusChoices.ready, StatusChoices.finished]).filter(current_privacy=PrivacyChoices.public)

class SlateCreateView(LoginRequiredMixin, generic.edit.CreateView):
    model = Slate
    form_class = SlateForm

    def get_form_kwargs(self):
        form_kws = super(SlateCreateView, self).get_form_kwargs()
        form_kws["user"] = self.request.user
        form_kws["formtype"] = "create"
        return form_kws

    def get_success_url(self, **kwargs):
        return self.object.get_absolute_url()

    def get(self, request, *args, **kwargs):
        if not request.user.profile.verified and len(request.user.slate_set.all()) > 5:
            return render(request, 'invites/verification_limit.html', {'slates': True})
        else:
            return super(SlateCreateView, self).get(request, *args, **kwargs)

class SlateEditView(UserPassesTestMixin, generic.edit.UpdateView):
    model = Slate
    form_class = SlateForm

    def get_form_kwargs(self):
        form_kws = super(SlateEditView, self).get_form_kwargs()
        form_kws["user"] = self.request.user
        form_kws["formtype"] = "update"
        return form_kws

    def get_success_url(self, **kwargs):
        return self.object.get_absolute_url()

    def test_func(self):
        obj = self.get_object()
        return obj.creator == self.request.user

@login_required
def manage_action_for_slate(request, pk):
    sar = SlateActionRelationship.objects.get(pk=pk)
    if request.method == 'POST':
        form = SlateActionRelationshipForm(request.POST)
        if form.is_valid():
            sar.priority = form.cleaned_data['priority']
            sar.status = form.cleaned_data['status']
            sar.notes = form.cleaned_data['notes']
            sar.save()
            return HttpResponseRedirect(reverse('slate', kwargs={'slug':sar.slate.slug}))
        else:
            context = {'form': form, 'sar': sar }
            render(request, 'slates/manage_action_for_slate.html', context)
    else:
        form = SlateActionRelationshipForm(initial={'priority': sar.priority, 'status': sar.status, 'notes': sar.notes})
        context = {'form': form, 'sar': sar}
        return render(request, 'slates/manage_action_for_slate.html', context)

class FollowUsersAndSlates(LoginRequiredMixin, generic.TemplateView):
    template_name = "slates/follow_users_and_slates.html"

    def get_context_data(self, **kwargs):
        context = super(FollowUsersAndSlates, self).get_context_data(**kwargs)
        rectracker = RecommendationTracker.objects.first()
        if rectracker:
            context['users'] = rectracker.retrieve_users()
            context['slates'] = rectracker.retrieve_slates()
        return context
