from __future__ import unicode_literals

from django.db import models
from django.core.urlresolvers import reverse
from django.utils import timezone
from ckeditor.fields import RichTextField
from mysite.lib.utils import slug_validator, slugify_helper

class Post(models.Model):
    slug = models.CharField(max_length=50, unique=True, blank=True, validators=slug_validator)
    title = models.CharField(max_length=300)
    summary = models.CharField(max_length=500)
    description = RichTextField(max_length=5000, blank=True, null=True)
    date_created = models.DateTimeField(default=timezone.now)
    date_updated = models.DateTimeField(blank=True, null=True)

    def __unicode__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.pk:
            self.slug = slugify_helper(Post, self.title)
        super(Post, self).save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('blog_post', kwargs={'slug': self.slug})

    def get_summary(self):
        if self.summary:
            return self.summary
        if len(self.description) > 200:
            return self.description[:200]
        return self.description
