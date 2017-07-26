from django.conf.urls import url

from groups import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^groups/$', views.GroupListView.as_view(), name='groups'),
    url(r'^group/(?P<slug>[-\w]+)/$', views.GroupView.as_view(), name='group'),
    url(r'^edit/(?P<slug>[-\w]+)/$', views.GroupEditView.as_view(), name='edit_group'),
    url(r'^admin/(?P<slug>[-\w]+)/$', views.GroupAdminView.as_view(), name='admin_group'),
    url(r'^create/$', views.GroupCreateView.as_view(), name='create_group'),
]
