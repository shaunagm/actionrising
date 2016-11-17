from django.shortcuts import render
from django.http import HttpResponse
from django.views import generic

def index(request):
    # Redirect to about page until we've  got a better landing page
    return render(request, 'mysite/about.html')
    # return render(request, 'mysite/base.html')

def about(request):
    return render(request, 'mysite/about.html')
