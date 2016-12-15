from itertools import chain

from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.views import generic
from django.contrib.auth.mixins import UserPassesTestMixin,  LoginRequiredMixin
from django.contrib.auth.decorators import login_required

from mysite.utils import check_privacy, filter_list_for_privacy, filter_list_for_privacy_annotated
from django.contrib.auth.models import User
from actions.models import Action, ActionTopic, ActionType, Slate, SlateActionRelationship
from actions.forms import ActionForm, SlateForm, SlateActionRelationshipForm

@login_required
def index(request):
    return HttpResponseRedirect(reverse('actions'))

class ActionView(UserPassesTestMixin, generic.DetailView):
    template_name = 'actions/action.html'
    model = Action

    def get_context_data(self, **kwargs):
        context = super(ActionView, self).get_context_data(**kwargs)
        context['topic_or_type_list'] = self.object.get_tags()
        context['trackers'] = filter_list_for_privacy_annotated(self.object.profile_set.all(), self.request.user)
        context['slates'] = filter_list_for_privacy_annotated(self.object.slate_set.all(), self.request.user)
        if self.request.user.is_authenticated():
            context['par'] = self.request.user.profile.get_par_given_action(self.object)
        context['flag'] = self.object.is_flagged_by_user(self.request.user, new_only=False)
        return context

    def test_func(self):
        obj = self.get_object()
        return check_privacy(obj, self.request.user)

class ActionListView(LoginRequiredMixin, generic.ListView):
    template_name = "actions/actions.html"
    model = Action
    queryset = Action.objects.filter(status__in=["rea", "fin"]).filter(current_privacy__in=["pub", "sit"])

class PublicActionListView(generic.ListView):
    template_name = "actions/actions.html"
    model = Action
    queryset = Action.objects.filter(status__in=["rea", "fin"]).filter(current_privacy="pub")

def create_action_helper(object, types, topics, user):
    object.creator = user
    object.save()
    for atype in types:
        object.actiontypes.add(atype)
    for topic in topics:
        object.topics.add(topic)
    return object

class ActionCreateView(LoginRequiredMixin, generic.edit.CreateView):
    model = Action
    form_class = ActionForm

    def get_form_kwargs(self):
        form_kws = super(ActionCreateView, self).get_form_kwargs()
        form_kws["user"] = self.request.user
        return form_kws

    def form_valid(self, form):
        types = form.cleaned_data.pop('actiontypes')
        topics = form.cleaned_data.pop('topics')
        object = form.save(commit=False)
        self.object = create_action_helper(object, types, topics, self.request.user)
        return super(ActionCreateView, self).form_valid(form)

    def get_success_url(self, **kwargs):
        return self.object.get_absolute_url()

class ActionEditView(UserPassesTestMixin, generic.edit.UpdateView):
    model = Action
    form_class = ActionForm

    def test_func(self):
        obj = self.get_object()
        return obj.creator == self.request.user

    def get_form_kwargs(self):
        form_kws = super(ActionEditView, self).get_form_kwargs()
        form_kws["user"] = self.request.user
        return form_kws

class TopicView(LoginRequiredMixin, generic.DetailView):
    template_name = 'actions/type_or_topic.html'
    model = ActionTopic

    def get_context_data(self, **kwargs):
        context = super(TopicView, self).get_context_data(**kwargs)
        context['action_list'] = filter_list_for_privacy(self.object.actions_for_topic.all(),
            self.request.user)
        return context

class TopicListView(LoginRequiredMixin, generic.ListView):
    template_name = "actions/topics.html"
    model = ActionTopic

class TypeView(LoginRequiredMixin, generic.DetailView):
    template_name = 'actions/type_or_topic.html'
    model = ActionType

    def get_context_data(self, **kwargs):
        context = super(TypeView, self).get_context_data(**kwargs)
        context['action_list'] = filter_list_for_privacy(self.object.actions_for_type.all(),
            self.request.user)
        return context

class TypeListView(LoginRequiredMixin, generic.ListView):
    template_name = "actions/types.html"
    model = ActionType

class SlateView(UserPassesTestMixin, generic.DetailView):
    template_name = 'actions/slate.html'
    model = Slate

    def get_context_data(self, **kwargs):
        context = super(SlateView, self).get_context_data(**kwargs)
        context['has_notes'] = True
        context['can_edit_actions'] = True if self.object.creator == self.request.user else False
        context['is_slate'] = True
        context['flag'] = self.object.is_flagged_by_user(self.request.user, new_only=False)
        annotated_list = filter_list_for_privacy_annotated(self.object.slateactionrelationship_set.all(),
            self.request.user)
        context['actions'] = annotated_list['public_list']
        context['hidden_actions'] = annotated_list['anonymous_count']
        return context

    def test_func(self):
        obj = self.get_object()
        return check_privacy(obj, self.request.user)

class SlateListView(LoginRequiredMixin, generic.ListView):
    # Note: templates can likely be refactored to use same template as TopicListView
    template_name = "actions/slates.html"
    model = Slate
    queryset = Slate.objects.filter(status__in=["rea", "fin"]).filter(current_privacy__in=["pub", "sit"])

def create_slate_helper(object, actions, user):
    object.creator = user
    object.save()
    for action in actions:
        SlateActionRelationship.objects.create(slate=object, action=action)
    return object

class SlateCreateView(LoginRequiredMixin, generic.edit.CreateView):
    model = Slate
    form_class = SlateForm

    def get_form_kwargs(self):
        form_kws = super(SlateCreateView, self).get_form_kwargs()
        form_kws["user"] = self.request.user
        return form_kws

    def form_valid(self, form):
        actions = form.cleaned_data.pop('actions')
        object = form.save(commit=False)
        self.object = create_slate_helper(object, actions, self.request.user)
        return super(SlateCreateView, self).form_valid(form)

    def get_success_url(self, **kwargs):
        return self.object.get_absolute_url()

def edit_slate_helper(object, actions):
    for action in actions:
        if action not in object.actions.all():
            SlateActionRelationship.objects.create(slate=object, action=action)
    for action in object.actions.all():
        if action not in actions:
            sar = SlateActionRelationship.objects.get(slate=object, action=action)
            sar.delete()

class SlateEditView(UserPassesTestMixin, generic.edit.UpdateView):
    model = Slate
    form_class = SlateForm

    def get_form_kwargs(self):
        form_kws = super(SlateEditView, self).get_form_kwargs()
        form_kws["user"] = self.request.user
        return form_kws

    def form_valid(self, form):
        actions = form.cleaned_data.pop('actions')
        object = form.save(commit=False)
        self.object = edit_slate_helper(object, actions)
        return super(SlateEditView, self).form_valid(form)

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
            render(request, 'actions/manage_action_for_slate.html', context)
    else:
        form = SlateActionRelationshipForm(initial={'priority': sar.priority, 'status': sar.status, 'notes': sar.notes})
        context = {'form': form, 'sar': sar}
        return render(request, 'actions/manage_action_for_slate.html', context)
