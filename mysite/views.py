from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.views import generic
from django.core.urlresolvers import reverse

def index(request):
    # Redirect to about page until we've  got a better landing page
    return render(request, 'mysite/about.html')
    # return render(request, 'mysite/base.html')

def about(request):
    return render(request, 'mysite/about.html')

def change_password_redirect(request):
    return HttpResponseRedirect(reverse('profile', kwargs={'slug': request.user.username }))
