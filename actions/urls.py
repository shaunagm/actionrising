from django.conf.urls import url

from actions import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^actions/?$', views.ActionListView.as_view(), name='actions'),
    url(r'^public-actions/?$', views.PublicActionListView.as_view(), name='public-actions'),
    url(r'^action/(?P<slug>[-\w]+)$', views.ActionView.as_view(), name='action'),
    url(r'^create', views.ActionCreateView.as_view(), name='create_action'),
    url(r'^edit/(?P<slug>[-\w]+)$', views.ActionEditView.as_view(), name='edit_action'),
    url(r'^topics/?$', views.TopicListView.as_view(), name='topics'),
    url(r'^topic/(?P<slug>[-\w]+)$', views.TopicView.as_view(), name='topic'),
    url(r'^types/?$', views.TypeListView.as_view(), name='types'),
    url(r'^type/(?P<slug>[-\w]+)$', views.TypeView.as_view(), name='type'),
    url(r'^slates/?$', views.SlateListView.as_view(), name='slates'),
    url(r'^slate/(?P<slug>[-\w]+)$', views.SlateView.as_view(), name='slate'),
    url(r'^slate-create/?$', views.SlateCreateView.as_view(), name='create_slate'),
    url(r'^slate-edit/(?P<slug>[-\w]+)$', views.SlateEditView.as_view(), name='edit_slate'),
    url(r'^manage-action/(?P<pk>[0-9]+)/?$', views.manage_action_for_slate, name = "manage_action_for_slate"),

    # Set up a redirect so url/topic or url/topic/ with no slug provided goes to /topics
    # And same for types
]
