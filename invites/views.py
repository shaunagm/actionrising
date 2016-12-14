import random, string, datetime

from django.shortcuts import render
from django.views import generic
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseRedirect
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse

from mysite.utils import get_hash_given_request
from invites.models import Invite
from invites.forms import InviteForm, InviteFriendForm, CreateUserFromInviteForm

class RequestAccountView(generic.edit.CreateView):
    model = Invite
    form_class = InviteForm
    success_url = "/invites/sent"

    def form_valid(self, form):
        hashstring = get_hash_given_request(self.request)
        date_from = datetime.datetime.now() - datetime.timedelta(days=1)
        if Invite.objects.filter(requester_hash=hashstring).filter(initial_request_date__gte=date_from):
            return HttpResponseRedirect(reverse('sent-invite'))
        else:
            form.instance.requester_hash = hashstring
            form.instance.add_inviter(self.request.user.username)
            return super(RequestAccountView, self).form_valid(form)

def request_confirmation_view(request, slug):
    try:
        invite = Invite.objects.get(confirmation_url_string=slug)
        if invite.request_status != "emailed":
            return HttpResponseRedirect(reverse('generic_problem'))
        generated_password = ''.join(random.SystemRandom().choice(string.ascii_uppercase + string.digits) for _ in range(10))
        user = User.objects.create_user(username=invite.username, password=generated_password)
        invite.request_status = "done"
        invite.save()
    except:
        return HttpResponseRedirect(reverse('generic_problem'))
    return render(request, 'invites/request_confirmation.html', {
        'generated_password': generated_password,
        'username': user.username
    })

class InviteFriendView(LoginRequiredMixin, generic.edit.CreateView):
    model = Invite
    form_class = InviteFriendForm
    success_url = "/invites/sent"

    def form_valid(self, form):
        form.instance.add_inviter(self.request.user.username)
        return super(InviteFriendView, self).form_valid(form)

def invite_confirmation_view(request, slug):
    try:
        invite = Invite.objects.get(confirmation_url_string=slug)
        if request.method == 'POST':
            form = CreateUserFromInviteForm(request.POST)
            if form.is_valid(): # Save and go to confirmation page
                form.save(email=invite.email)
                invite.request_status = "done"
                invite.save()
                return render(request, 'invites/request_confirmation.html', {})
            else: # Return with errors
                context = {'form': form}
                render(request, 'invites/finish_invite_signup.html', context)
        else:
            if invite.request_status == "emailed":
                form = CreateUserFromInviteForm()
                context = {'form': form}
                return render(request, 'invites/finish_invite_signup.html', context)
    except:
        return HttpResponseRedirect(reverse('generic_problem'))
    return HttpResponseRedirect(reverse('generic_problem'))

class SentView(generic.TemplateView):
    template_name = "invites/sent_invite.html"

class GenericProblemView(generic.TemplateView):
    template_name = "invites/generic_problem.html"
