from datetime import date

from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.views import generic
from django.core.urlresolvers import reverse

def index(request):
    # Redirect to about page until we've  got a better landing page
    return render(request, 'mysite/landing.html')

def about(request):
    time_elapsed = (date.today() - date(2016, 11, 11)).days
    return render(request, 'mysite/about.html', {'time_elapsed': time_elapsed})

class PrivacyPolicyView(generic.TemplateView):
    template_name = "mysite/privacy_policy.html"

def change_password_redirect(request):
    return render(request, 'mysite/landing.html')

def acme_challenge(request):
    return render(request, 'mysite/challenge.html')

def acme_challenge2(request):
    return render(request, 'mysite/challenge2.html')
