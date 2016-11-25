from django.conf.urls import url

from profiles import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^profiles$', views.ProfileSearchView.as_view(), name='profiles'),
    url(r'^profile/(?P<slug>[-\w]+)$', views.ProfileView.as_view(), name='profile'),
    url(r'^to-do/(?P<slug>[-\w]+)$', views.ProfileToDoView.as_view(), name='to_do'),
    url(r'^edit/(?P<pk>[-\w]+)$', views.ProfileEditView.as_view(), name='edit_profile'),
    url(r'^toggle/(?P<username>[-\w]+)/(?P<toggle_type>[-\w]+)$', views.toggle_relationships, name='toggle_relationships'),
    url(r'^toggle-action/(?P<slug>[-\w]+)/(?P<toggle_type>[-\w]+)$', views.toggle_action_for_profile, name = "toggle_action_for_profile"),
    url(r'^manage-action/(?P<slug>[-\w]+)/?$', views.manage_action, name = "manage_action_for_profile"),
    url(r'^mark_as_done/(?P<slug>[-\w]+)/(?P<mark_as>[-\w]+)?$', views.mark_as_done, name = "mark_as_done"),
]
