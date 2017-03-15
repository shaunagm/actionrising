from __future__ import unicode_literals

import datetime, pytz, json
from django.utils import timezone

from django.contrib.auth.models import User
from actstream.models import Follow
from django.db import models
from profiles.models import Profile, ProfileActionRelationship, Relationship
from actions.models import Action
from slates.models import Slate
from mysite.lib.choices import PrivacyChoices


# Create your models here.
class RecommendationTracker(models.Model):
    """ Stores recommendations to prevent multiple DB hits"""
    # Recommended Users
    users_last_updated = models.DateTimeField(default=timezone.now)
    users_update_after = models.IntegerField(default=300) # Integer represents before minutes
    users_recommended = models.CharField(max_length=300)
    # Recommended Slates
    slates_last_updated = models.DateTimeField(default=timezone.now)
    slates_update_after = models.IntegerField(default=300)
    slates_recommended = models.CharField(max_length=300)

    def set_users(self, pks):
        self.users_recommended = json.dumps(pks)
        self.save()

    def get_users(self):
        if not self.users_recommended:
            self.calculate_recommended_users()
        return json.loads(self.users_recommended)

    # NOTE: This should be a management command, otherwise it will *always* delay a page load
    def retrieve_users(self):
        seconds_elapsed = (datetime.datetime.now(tz=pytz.utc) - self.users_last_updated).seconds
        if (seconds_elapsed * 60) > self.users_update_after:
            self.calculate_recommended_users()
        return [user for user in User.objects.filter(pk__in=self.get_users())]

    def calculate_recommended_users(self):
        # Get creators of up to 15 most popular actions
        actions = Action.objects.all().annotate(followers=models.Count('profileactionrelationship',
            distinct=True)).order_by('-followers')
        popular_action_creators = [action.creator for action in actions]
        if len(popular_action_creators) > 15:
            popular_action_creators = popular_action_creators[:15]
        # Get creators of up to 15 most popular slates
        slates = Slate.objects.all().annotate(followers=models.Count('slateactionrelationship',
            distinct=True)).order_by('-followers')
        popular_slate_creators = [slate.creator for slate in slates]
        if len(popular_slate_creators) > 15:
            popular_slate_creators = popular_slate_creators[:15]
        creators = list(set(popular_slate_creators + popular_action_creators))
        creators = [creator.pk for creator in creators if creator.profile.current_privacy == PrivacyChoices.public]
        print("privacyfilled: ", creators)
        if len(creators) > 20:
            creators = random.sample(creators, 20)
        self.set_users(creators)
        self.users_last_updated = datetime.datetime.now(tz=pytz.utc)
        self.save()

    def set_slates(self, pks):
        self.slates_recommended = json.dumps(pks)
        self.save()

    def get_slates(self):
        if self.slates_recommended:
            return json.loads(self.slates_recommended)

    def retrieve_slates(self):
        # Handpick for now, while there are so few slates
        return [slate for slate in Slate.objects.filter(pk__in=self.get_slates())]
