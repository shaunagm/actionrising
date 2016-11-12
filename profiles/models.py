from __future__ import unicode_literals
from django.db import models
from django.db.models.signals import post_save
from django.core.urlresolvers import reverse

from django.contrib.auth.models import User

class Profile(models.Model):
    user = models.OneToOneField(User, unique=True)
    verified = models.BooleanField(default=False)
    text = models.CharField(max_length=500, blank=True, null=True)  # Rich text?
    location = models.CharField(max_length=140, blank=True, null=True)
    links = models.CharField(max_length=400, blank=True, null=True)
    connections = models.ManyToManyField('self', through='Relationship',
                                           symmetrical=False,
                                           related_name='connected_to')

    def __unicode__(self):
        return u'Profile of user: %s' % self.user.username

    def get_absolute_url(self):
        return reverse('profile', kwargs={'slug': self.user.username })

    def get_edit_url(self):
        return reverse('edit_profile', kwargs={'pk': self.pk })

    # Add methods to save and access links as json objects

    # Add links to get specific kinds of links, so that Twitter for instance can be displayed with the
    # Twitter image

    # Add methods to display actions data linked from actions app

    # Add methods to facilitate viewing on friendfeeds

def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

post_save.connect(create_user_profile, sender=User)

class Relationship(models.Model):
    person_from = models.ForeignKey(User, related_name='from_people')
    person_to = models.ForeignKey(User, related_name='to_people')
    RELATIONSHIP_CHOICES = (
        ('fol', 'Following'),
        ('bud', 'Buddy'),
    )
    kind = models.CharField(max_length=3, choices=RELATIONSHIP_CHOICES, default='fol')
    mute = models.BooleanField(default=False)

class PrivacyDefaults(models.Model):
    user = models.OneToOneField(User, unique=True)
    PRIVACY_CHOICES = (
        ('pub', 'Visible to Public'),
        ('sit', 'Visible Sitewide'),
        ('fol', 'Visible to Buddies and Those You Follow'),
        ('bud', 'Visible to Buddies'),
        ('you', 'Only Visible to You'),
    )
    global_default = models.CharField(max_length=3, choices=PRIVACY_CHOICES, default='fol')
