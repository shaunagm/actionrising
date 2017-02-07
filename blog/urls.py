from django.conf.urls import url

from blog import views
from blog.feeds import LatestEntriesFeed

urlpatterns = [
    url(r'^$', views.BlogPostListView.as_view(), name='blog_posts'),
    url(r'^post/(?P<slug>[-\w]+)$', views.BlogPostView.as_view(), name='blog_post'),
    url(r'^feed/$', LatestEntriesFeed()),
]
