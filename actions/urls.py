from django.conf.urls import url

from actions import views

urlpatterns = [
    url(r'^$', views.IndexView.as_view(), name='index'),
    url(r'^action/(?P<slug>[-\w]+)$', views.ActionView.as_view(), name='action'),
    url(r'^create', views.ActionCreateView.as_view(), name='create_action'),
    url(r'^edit/(?P<slug>[-\w]+)$', views.ActionEditView.as_view(), name='edit_action'),
    url(r'^topics/?$', views.TopicListView.as_view(), name='topics'),
    url(r'^topic/(?P<slug>[-\w]+)$', views.TopicView.as_view(), name='topic'),
    url(r'^types/?$', views.TypeListView.as_view(), name='types'),
    url(r'^type/(?P<slug>[-\w]+)$', views.TypeView.as_view(), name='type'),
    # Set up a redirect so url/topic or url/topic/ with no slug provided goes to /topics
    # And same for types
]
