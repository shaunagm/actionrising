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
    # Redirects
    url(r'^slate/(?P<slug>[-\w]+)$', views.SlateRedirectView.as_view(), name='slate_redirect'),

    # Set up a redirect so url/topic or url/topic/ with no slug provided goes to /topics
    # And same for types
]
