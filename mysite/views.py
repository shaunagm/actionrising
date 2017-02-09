from datetime import date

from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.views import generic
from django.core.urlresolvers import reverse

def index(request):
    if request.user.is_authenticated():
        return HttpResponseRedirect(request.user.navbarsettings.get_landing_url_from_index())
    return render(request, 'mysite/landing.html')

def about(request):
    return render(request, 'mysite/about.html')

class PrivacyPolicyView(generic.TemplateView):
    template_name = "mysite/privacy_policy.html"

def change_password_redirect(request):
    return HttpResponseRedirect(reverse('index'))

def acme_challenge(request):
    return render(request, 'mysite/challenge.html')

def acme_challenge2(request):
    return render(request, 'mysite/challenge2.html')
