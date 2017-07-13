from django.contrib.syndication.views import Feed
from django.urls import reverse
from blog.models import Post

from mysite.constants import constants_table

class LatestEntriesFeed(Feed):
    title = "{} Blog".format(constants_table['SITE_NAME'])
    link = "/posts/"
    description = "News, new features and more from {}.com".format(constants_table['SITE_NAME'])

    def items(self):
        return Post.objects.order_by('-date_created')[:10]

    def item_title(self, item):
        return item.title

    def item_description(self, item):
        return item.description
