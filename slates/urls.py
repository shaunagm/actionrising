from django.conf.urls import url

from slates import views

urlpatterns = [
    url(r'^slates/$', views.SlateListView.as_view(), name='slates'),
    url(r'^slate/(?P<slug>[-\w]+)/$', views.SlateView.as_view(), name='slate'),
    url(r'^slate-create/$', views.SlateCreateView.as_view(), name='create_slate'),
    url(r'^slate-edit/(?P<slug>[-\w]+)/$', views.SlateEditView.as_view(), name='edit_slate'),
    url(r'^manage-action/(?P<pk>[0-9]+)/$', views.manage_action_for_slate, name = "manage_action_for_slate"),
    url(r'^community/$', views.FollowUsersAndSlates.as_view(), name='community'),
]
