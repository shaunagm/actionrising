from django.conf.urls import url

from profiles import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^profiles$', views.ProfileSearchView.as_view(), name='profiles'),
    url(r'^profile/(?P<slug>[-\w]+)$', views.ProfileView.as_view(), name='profile'),
    url(r'^dashboard$', views.DashboardView.as_view(), name='dashboard'),
    url(r'^todo/$', views.ToDoView.as_view(), name='to_do'),
    url(r'^feed/$', views.FeedView.as_view(), name='feed'),
    url(r'^activity/$', views.ActivityView.as_view(), name='activity'),
    url(r'^suggested/(?P<slug>[-\w]+)$', views.ProfileSuggestedView.as_view(), name='suggested'),
    url(r'^edit/(?P<slug>[-\w]+)$', views.ProfileEditView.as_view(), name='edit_profile'),
    url(r'^toggle/(?P<slug>[-\w]+)/(?P<toggle_type>[-\w]+)$', views.toggle_relationships, name='toggle_relationships'),
    url(r'^toggle-action/(?P<slug>[-\w]+)/(?P<toggle_type>[-\w]+)$', views.toggle_action_for_profile, name = "toggle_action_for_profile"),
    url(r'^manage-action/(?P<slug>[-\w]+)/?$', views.manage_action, name = "manage_action_for_profile"),
    url(r'^toggle-slate/(?P<slug>[-\w]+)/(?P<toggle_type>[-\w]+)$', views.toggle_slate_for_profile, name = "toggle_slate_for_profile"),
    url(r'^manage-suggested-action/(?P<slug>[-\w]+)/(?P<type>[-\w]+)$', views.manage_suggested_action, name = "manage_suggested_action"),
    url(r'^mark_as_done/(?P<slug>[-\w]+)/(?P<mark_as>[-\w]+)?$', views.mark_as_done, name = "mark_as_done"),
]
