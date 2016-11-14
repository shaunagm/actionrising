from django.conf.urls import url

from profiles import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^profiles$', views.ProfileSearchView.as_view(), name='profile_search'),
    url(r'^profile/(?P<slug>[-\w]+)$', views.ProfileView.as_view(), name='profile'),
    url(r'^edit/(?P<pk>[-\w]+)$', views.ProfileEditView.as_view(), name='edit_profile'),
]
