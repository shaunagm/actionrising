from factory.django import DjangoModelFactory
import factory.faker

from . import models


class Profile(factory.Factory):
    class Meta:
        model = models.Profile

    user = factory.SubFactory("accounts.factories.User", profile=None)

    @classmethod
    def _generate(cls, create, attrs):
        # profile is created in post_save and can't pass attrs into it
        return attrs['user'].profile


class RelationShip(DjangoModelFactory):
    class Meta:
        model = models.Relationship

    person_A = factory.SubFactory(Profile)
    person_B = factory.SubFactory(Profile)


class ProfileSlateRelationship(DjangoModelFactory):
    class Meta:
        model = models.ProfileSlateRelationship

    profile = factory.SubFactory(Profile)
    slate = factory.SubFactory("slates.factories.Slate")


class ProfileActionRelationship(DjangoModelFactory):
    class Meta:
        model = models.ProfileActionRelationship

    profile = factory.SubFactory(Profile)
    action = factory.SubFactory("actions.factories.Action")
    last_suggester = factory.SelfAttribute("profile.user")
