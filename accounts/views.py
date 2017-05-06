from django.shortcuts import render, redirect
from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth import login
from django.contrib.auth.models import User
from django.views import generic
from django.utils.http import urlsafe_base64_decode
from django.utils.encoding import force_text
from django.contrib.auth.mixins import LoginRequiredMixin

from social_django.models import UserSocialAuth

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

class SettingsView(LoginRequiredMixin, generic.TemplateView):
    template_name = 'accounts/account_settings.html'

    def get_context_data(self, **kwargs):
        context = super(SettingsView, self).get_context_data(**kwargs)
        user = self.request.user
        try:
            context['twitter_login'] = user.social_auth.get(provider='twitter')
        except UserSocialAuth.DoesNotExist:
            pass
        try:
            context['facebook_login'] = user.social_auth.get(provider='facebook')
        except UserSocialAuth.DoesNotExist:
            pass
        try:
            context['google_login'] = user.social_auth.get(provider='google-oauth2')
        except UserSocialAuth.DoesNotExist:
            pass

        if user.social_auth.count() > 1 or (user.has_usable_password() and user.email):
            context['can_disconnect'] = True

        return context
