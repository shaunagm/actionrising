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

    # Site info pages
    url(r'^learn-more/$', views.LearnMoreView.as_view(), name='learn-more'),
    url(r'^privacy-policy$', views.PrivacyPolicyView.as_view(), name='privacy-policy'),
    url(r'^about/$', views.about, name='about'),

    # Links to apps
    url(r'^actions/', include('actions.urls')),
    url(r'^profiles/', include('profiles.urls')),
    url(r'^accounts/', include('accounts.urls')),
    url(r'^specialactions/', include('plugins.urls')),
    url(r'^slates/', include('slates.urls')),
    url(r'^groups/', include('groups.urls')),
    url(r'^tags/', include('tags.urls')),
    url(r'^flags/', include('flags.urls')),
    url(r'^blog/', include('blog.urls')),
    url(r'^notifications/', include('notifications.urls')),
    url(r'^comments/', include('django_comments.urls')),
    url(r'^commitments/', include('commitments.urls')),
    url(r'^admin/', admin.site.urls),

    # Third party apps
    url(r'^django-rq/', include('django_rq.urls')),
    url(r'^oauth/', include('social_django.urls', namespace='social')),
    url('^activity/', include('actstream.urls')),

    # Index
    url(r'^$', views.index, name='index'),
]

handler404 = 'mysite.views.custom_404'
handler500 = 'mysite.views.custom_500'
