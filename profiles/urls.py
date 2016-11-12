from django.conf.urls import url

from profiles import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^(?P<slug>[-\w]+)$', views.ProfileView.as_view(), name='profile'),
]
