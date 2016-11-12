from django.conf.urls import url

from actions import views

urlpatterns = [
    url(r'^$', views.IndexView.as_view(), name='index'),
    url(r'^(?P<slug>[-\w]+)$', views.ActionView.as_view(), name='action'),
]
