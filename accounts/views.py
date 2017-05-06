from django.shortcuts import render, redirect
from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth import login
from django.contrib.auth.models import User
from django.views import generic
from django.utils.http import urlsafe_base64_decode
from django.utils.encoding import force_text

from accounts.lib.tokens import account_activation_token
from accounts.forms import SignUpForm

# Sign up views

class SignUpView(generic.edit.CreateView):
    model = User
    form_class = SignUpForm
    template_name = "accounts/signup_form.html"
    success_url = "/accounts/sent"

class SentView(generic.TemplateView):
    template_name = "accounts/sent_invite.html"

def confirmation(request, uidb64, token):
    try:
        uid = force_text(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except:
        user = None

    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.save()
        login(request, user)
        return redirect('index')
    else:
        print("User confirmation error uidb64 %s token %s" % (uidb64, token))
        return render(request, 'accounts/generic_problem.html')

# Login/logout views

# Change password views

def change_password_redirect(request):
    return HttpResponseRedirect(reverse('index'))
