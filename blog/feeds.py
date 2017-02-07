from django.contrib.syndication.views import Feed
from django.urls import reverse
from blog.models import Post

class LatestEntriesFeed(Feed):
    title = "ActionRising Blog"
    link = "/posts/"
    description = "News, new features and more from ActionRising.com"

    def items(self):
        return Post.objects.order_by('-date_created')[:10]

    def item_title(self, item):
        return item.title

    def item_description(self, item):
        return item.description
