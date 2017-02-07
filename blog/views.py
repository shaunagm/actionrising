from django.views import generic
from blog.models import Post

class BlogPostView(generic.DetailView):
    template_name = "blog/post.html"
    model = Post

class BlogPostListView(generic.ListView):
    template_name = "blog/post_list.html"
    model = Post
