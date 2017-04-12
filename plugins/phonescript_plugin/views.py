from django.shortcuts import render
from django.views import generic
from django.http import HttpResponseRedirect

from actions.models import Action
from actions.views import ActionEditView, ActionCreateView, ActionView

from plugins.phonescript_plugin.models import PhoneScript, ScriptMatcher
from plugins.phonescript_plugin.forms import (DefaultForm, ConstituentFormset,
    UniversalFormset, LegislatorPositionForm)
from plugins.phonescript_plugin.lib import phonescripts

def lookup_helper(action, lookup):
    if lookup == "default":
        return phonescripts.get_default_scripts(action), "Success"
    else:
        # Lookup using this location.
        reps = phonescripts.get_reps_from_select(lookup)
        if reps:
            # If successful, return that
            return phonescripts.get_all_scripts(action, legs=reps), "Success"
        else:
            # Otherwise, return error msg
            return [], "Error"

class PhoneScriptView(ActionView):
    template_name = "phonescript_plugin/action.html"

    def get_context_data(self, **kwargs):
        context = super(PhoneScriptView, self).get_context_data(**kwargs)
        # Are we coming here via temporary location or explicit "no location"
        lookup = self.kwargs.get('lookup', None)
        if lookup:
            context['scripts'], context['status'] = lookup_helper(self.object, lookup)
            return context
        # If not, this is the first time through, so check status:
        status, location = phonescripts.get_user_status(self.request.user)
        if not location:
            context['status'] = status
        else:
            context['status'] = "Success"
            context['scripts'] = phonescripts.get_all_scripts(self.get_object(), location)
        return context

class PhoneScriptCreateView(ActionCreateView):
    template_name = "phonescript_plugin/action_form.html"

    def get_context_data(self, default_form=DefaultForm(prefix="def"),
        constituent_forms=ConstituentFormset(prefix="con", queryset=PhoneScript.objects.none()),
        universal_forms=UniversalFormset(prefix="uni", queryset=PhoneScript.objects.none()), **kwargs):
        context = super(PhoneScriptCreateView, self).get_context_data(**kwargs)
        context['default_form'] = default_form
        context['constituent_forms'] = constituent_forms
        context['universal_forms'] = universal_forms
        return context

    def post(self, request, *args, **kwargs):
        # Get action form
        self.object = None
        form_class = self.get_form_class()
        form = self.get_form(form_class)
        # Get additional forms
        default_form = DefaultForm(self.request.POST, prefix="def")
        constituent_forms = ConstituentFormset(self.request.POST, prefix="con")
        universal_forms = UniversalFormset(self.request.POST, prefix="uni")
        if (form.is_valid() and default_form.is_valid() and constituent_forms.is_valid() and
            universal_forms.is_valid()):
            return self.form_valid(form, default_form, constituent_forms, universal_forms)
        else:
            return self.form_invalid(form, default_form, constituent_forms, universal_forms)

    def form_valid(self, form, default_form, constituent_forms, universal_forms):
        self.object = form.save()
        default_form.save(action=self.object)
        for cform in constituent_forms:
            if cform.has_changed():
                cform.save(action=self.object)
        for uform in universal_forms:
            if uform.has_changed():
                uform.save(action=self.object)
        phonescripts.create_initial_script_matches(self.object)
        return HttpResponseRedirect(self.get_success_url())

    def form_invalid(self, form, default_form, constituent_forms, universal_forms):
        return self.render_to_response(
            self.get_context_data(form=form,
                default_form=default_form,
                constituent_forms=constituent_forms,
                universal_forms=universal_forms))

class PhoneScriptEditView(ActionEditView):
    template_name = "phonescript_plugin/action_form.html"

    def get_context_data(self, **kwargs):
        context = super(PhoneScriptEditView, self).get_context_data(**kwargs)
        action = self.get_object()
        # Search for constituent scripts and prefill
        cqs = PhoneScript.objects.filter(action=action, script_type="constituent")
        cqs = cqs if cqs else PhoneScript.objects.none()
        context['constituent_forms'] = ConstituentFormset(prefix="con", queryset=cqs)
        # Search for universal scripts and prefill
        uqs = PhoneScript.objects.filter(action=action, script_type="universal")
        uqs = uqs if uqs else PhoneScript.objects.none()
        context['universal_forms'] = UniversalFormset(prefix="uni", queryset=uqs)
        # Search for default script and prefill
        df = PhoneScript.objects.filter(action=action, script_type="default")
        if df:
            context['default_form'] = DefaultForm(prefix="def", instance=df.first())
        else:
            self.initial_df = None
            context['default_form'] = DefaultForm(prefix="def")
        return context

    def post(self, request, *args, **kwargs):
        # Get action form
        self.object = self.get_object()
        form_class = self.get_form_class()
        form = self.get_form(form_class)
        # Get additional forms
        df = PhoneScript.objects.filter(action=self.object, script_type="default")
        initial_data = df.first() if df else None
        default_form = DefaultForm(self.request.POST, prefix="def", instance=initial_data)
        constituent_forms = ConstituentFormset(self.request.POST, prefix="con")
        universal_forms = UniversalFormset(self.request.POST, prefix="uni")
        if (form.is_valid() and default_form.is_valid() and constituent_forms.is_valid() and
            universal_forms.is_valid()):
            return self.form_valid(form, default_form, constituent_forms, universal_forms)
        else:
            return self.form_invalid(form, default_form, constituent_forms, universal_forms)

    def form_valid(self, form, default_form, constituent_forms, universal_forms):
        self.object = form.save()
        if default_form.has_changed():
            default_form.save(action=self.object)
        for cform in constituent_forms:
            if cform.has_changed():
                cform.save(action=self.object)
        for uform in universal_forms:
            if uform.has_changed():
                uform.save(action=self.object)
        return HttpResponseRedirect(self.get_success_url())

    def form_invalid(self, form, default_form, constituent_forms, universal_forms):
        return self.render_to_response(
            self.get_context_data(form=form,
                default_form=default_form,
                constituent_forms=constituent_forms,
                universal_forms=universal_forms))

class LegislatorPositionView(generic.list.ListView):
    model = ScriptMatcher
    template_name = "phonescript_plugin/legislator_position_view.html"

    def get_context_data(self, **kwargs):
        context = super(LegislatorPositionView, self).get_context_data(**kwargs)
        action = Action.objects.get(slug=self.kwargs['slug'])
        context['object'] = action
        context['action'] = action
        context['object_list'] = ScriptMatcher.objects.filter(action=action)
        return context

class LegislatorPositionEditView(generic.edit.FormView):
    template_name = "phonescript_plugin/legislator_position_edit_view.html"
    form_class = LegislatorPositionForm
    success_url = "" # Override below

    def get_form_kwargs(self):
        kwargs = super(LegislatorPositionEditView, self).get_form_kwargs()
        kwargs.update({'action_slug': self.kwargs['slug']})
        return kwargs

    def get_context_data(self, **kwargs):
        context = super(LegislatorPositionEditView, self).get_context_data(**kwargs)
        # This is a hack to deal with assumptions that action.html will only be called
        # from an action detailview
        action = Action.objects.get(slug=self.kwargs['slug'])
        context['object'] = action
        context['action'] = action
        return context

    def save_item(self, item):
        print(item)
        
        # ScriptMatcher.objects.filter()

    def post(self, request, *args, **kwargs):
        action = Action.objects.get(slug=self.kwargs['slug'])
        for item in request.POST:
            try:
                self.save_item(item, action)
            except:
                pass
        return HttpResponseRedirect(action.get_absolute_url())
