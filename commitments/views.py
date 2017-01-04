from django.shortcuts import render
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.views import generic

from actions.models import Action
from commitments.models import Commitment
from commitments.forms import CommitmentForm

class NewCommitmentView(LoginRequiredMixin, generic.edit.CreateView):
    model = Commitment
    form_class = CommitmentForm

    def get_form_kwargs(self):
        kwargs = super(NewCommitmentView, self).get_form_kwargs()
        kwargs['user'] = self.request.user
        kwargs['action'] = Action.objects.get(slug=self.kwargs['slug'])
        return kwargs

    def get_success_url(self):
        return self.object.action.get_absolute_url()

class EditCommitmentView(LoginRequiredMixin, generic.UpdateView):
    model = Commitment
    form_class = CommitmentForm

    def get_success_url(self):
        return self.object.action.get_absolute_url()

@login_required
def delete_commitment(request, pk):
    c = Commitment.objects.get(pk=pk)
    success_url = c.action.get_absolute_url()
    c.delete()
    return HttpResponseRedirect(success_url)
