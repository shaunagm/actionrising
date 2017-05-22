import mock
from factory.django import DjangoModelFactory
from faker.providers import BaseProvider
import factory.faker

from mysite.lib.choices import PrivacyChoices
from . import models


@factory.Faker.add_provider
class ActionRisingProvider(BaseProvider):
    def adjective(cls):
        return cls.random_element({
            "fluffy", "funny", "blue", "dogmatic", "cataclysmic", "interfaith",
            "indangered", "bad", "evil", "populist"
        })

    def generic_place(cls):
        return cls.random_element({
            "work", "the gym", "Applebees", "school", "jail", "summer camp",
            "court", "the airport",
        })

    def topic(cls):
        return cls.random_element({
            "cats", "hats", "puppies", "species"
        })

    def government_position(cls):
        return cls.random_element({
            "Senator", "Rep", "Congress-person", "Governor", "City Counselor"
        })

    def slate_title(self):
        pattern = self.random_element({
            'Advocating for {{adjective}} {{topic}}',
            'How to be {{adjective}} at {{generic_place}}',
            'Connecting with your {{government_position}} at {{generic_place}}',
        })
        return self.generator.parse(pattern)

    def action_title(self):
        pattern = self.random_element({
            'Advocating for {{adjective}} {{topic}}',
            'Call your {{adjective}} {{government_position}} about {{topic}}',
        })
        return self.generator.parse(pattern)


class Slate(DjangoModelFactory):
    class Meta:
        model = models.Slate
        # django_get_or_create = ("slug", )

    title = factory.Faker("slate_title")
    creator = factory.SubFactory("accounts.factories.User",
            profile=factory.SubFactory("profiles.factories.Profile"))
    description = factory.Faker("text")


class VisibleUnfollowedSlate(factory.Factory):
    class Meta:
        # trick to create random objects via factoryboy
        model = mock.Mock()

    slate = factory.SubFactory(Slate, privacy=PrivacyChoices.follows)
    relationship = factory.SubFactory('profiles.factories.Relationship',
        person_B=factory.SelfAttribute('..slate.creator.profile'),
        B_follows_A=True)


class SlateActionRelationship(DjangoModelFactory):
    class Meta:
        model = models.SlateActionRelationship

    slate = factory.SubFactory(Slate)
    action = factory.SubFactory("actions.factories.Action")
