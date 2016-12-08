"""mysite URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.10/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import include, url
from django.contrib import admin
from django.contrib.auth import views as auth_views

from mysite import views

urlpatterns = [
    url(r'^login/$', auth_views.login, {'template_name': 'profiles/login.html'}, name='login'),
    url(r'^logout/$', auth_views.logout, {'next_page': '/'}, name='logout'),
    url(r'^password/$', auth_views.password_change, {'template_name': 'mysite/password.html'}, name='password_reset'),
    url(r'^password/changed$', views.change_password_redirect, name='password_change_done'),
    url(r'^profiles/', include('profiles.urls')),
    url(r'^actions/', include('actions.urls')),
    url(r'^flags/', include('flags.urls')),
    url(r'^comments/', include('django_comments.urls')),
    url(r'^admin/', admin.site.urls),
    url(r'^about/?$', views.about, name='about'),
    url(r'^.well-known/acme-challenge/MdzRdJXytZiBN7PYPMUbU6HjvFP2aUDEN8saHRXGBCY', views.acme_challenge),
    url(r'^.well-known/acme-challenge/-_rzqfR-Q9sDxQqiKrK8naLr7nwmaCU2RbYS-hN-_Lc', views.acme_challenge2),
    url(r'^$', views.index, name='index'),
    url('^activity/', include('actstream.urls')),
]
