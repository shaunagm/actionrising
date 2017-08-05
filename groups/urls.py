from django.conf.urls import url

from groups import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^groups/$', views.GroupListView.as_view(), name='groups'),
    url(r'^group/(?P<slug>[-\w]+)/$', views.GroupView.as_view(), name='group'),
    url(r'^edit/(?P<slug>[-\w]+)/$', views.GroupEditView.as_view(), name='edit_group'),
    url(r'^admin/(?P<slug>[-\w]+)/$', views.GroupAdminView.as_view(), name='admin_group'),
    url(r'^create/$', views.GroupCreateView.as_view(), name='create_group'),
    url(r'^join_group/$', views.join_group, name='join_group'),
    url(r'^leave_group/$', views.leave_group, name='leave_group'),
    url(r'^remove_from_group/$', views.remove_from_group, name='remove_from_group'),
    url(r'^request_to_join_group/$', views.request_to_join_group, name='request_to_join_group'),
    url(r'^approve_request_to_join_group/$', views.approve_request_to_join_group,
        name='approve_request_to_join_group'),
    url(r'^invite_to_group/$', views.invite_to_group, name='invite_to_group'),
    url(r'^approve_invite_to_group/$', views.approve_invite_to_group,
        name='approve_invite_to_group'),
    url(r'^change_admin/$', views.change_admin, name='change_admin'),
]
