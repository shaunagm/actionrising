from datetime import date

from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.views import generic
from django.core.urlresolvers import reverse

def index(request):
    if request.user.is_authenticated():
        return HttpResponseRedirect(reverse('dashboard'))
    return render(request, 'mysite/landing.html')

def about(request):
    return render(request, 'mysite/about.html')

class LearnMoreView(generic.TemplateView):
    template_name = "actions/learn.html"

class PrivacyPolicyView(generic.TemplateView):
    template_name = "mysite/privacy_policy.html"

def custom_404(request):
    response = render(request, 'mysite/404.html')
    response.status_code = 404
    return response

def custom_500(request):
    response = render(request, 'mysite/500.html')
    response.status_code = 500
    return response
