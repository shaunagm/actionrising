import random, string, datetime

from django.shortcuts import render
from django.views import generic
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseRedirect
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse

from mysite.lib.utils import get_hash_given_request
from invites.models import Invite
from invites.forms import SignUpForm
from notifications.lib.email_handlers import generic_admin_email

class SignUpView(generic.edit.CreateView):
    model = Invite
    form_class = SignUpForm
    template_name = "invites/signup_form.html"
    success_url = "/invites/sent"

    def form_valid(self, form):
        hashstring = get_hash_given_request(self.request)
        date_from = datetime.datetime.now() - datetime.timedelta(hours=1)
        invites = Invite.objects.filter(requester_hash=hashstring).filter(initial_request_date__gte=date_from)
        # if invites:
        #     invite_strings = [invite.string_representation() for invite in invites]
        #     generic_admin_email("New account flagged as spam", ("---").join(invite_strings))
        #     return HttpResponseRedirect(reverse('sent-invite'))
        # else:
        form.instance.requester_hash = hashstring
        form.instance.add_inviter(self.request.user.username)
        form.instance.self_submitted = True
        return super(SignUpView, self).form_valid(form)

def signup_confirmation_view(request, slug):
    try:
        invite = Invite.objects.get(confirmation_url_string=slug)
        if invite.request_status != "emailed":
            return HttpResponseRedirect(reverse('generic_problem'))
        user = User.objects.get(username=invite.username)
        user.is_active = True
        user.save()
    except:
        return HttpResponseRedirect(reverse('generic_problem'))
    return render(request, 'invites/signup_confirmation.html')

class SentView(generic.TemplateView):
    template_name = "invites/sent_invite.html"

class GenericProblemView(generic.TemplateView):
    template_name = "invites/generic_problem.html"
