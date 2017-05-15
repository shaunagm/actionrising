from django.conf.urls import url

from tags import views

urlpatterns = [
    url(r'^$', views.TagListView.as_view(), name='all_tags'),
    url(r'^tag/(?P<slug>[-\w]+)/$', views.TagView.as_view(), name='tag'),
    url(r'^kind/(?P<kind>[-\w]+)/$', views.TagListView.as_view(), name='tags_by_kind'),
    # Set up a redirect so url/tag or url/tag/ with no slug provided goes to /tags
]
