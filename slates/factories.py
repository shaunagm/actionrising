from factory.django import DjangoModelFactory
from faker.providers import BaseProvider
import factory.faker

from . import models


@factory.Faker.add_provider
class SlateProvider(BaseProvider):
    def adjective(cls):
        return cls.random_element({
            "fluffy", "funny", "blue", "dogmatic", "cataclysmic", "interfaith",
            "indangered",
        })

    def topic(cls):
        return cls.random_element({
            "cats", "hats", "puppies", "species"
        })

    def government_position(cls):
        return cls.random_element({
            "Senator", "Rep", "Congress-person", "Governor", "City Counselor"
        })

    def title(self):
        pattern = self.random_element({
            'Advocating for {{adjective}} {{topic}}',
            'Call your {{adjective}} {{government_position}} about {{topic}}',
        })
        return self.generator.parse(pattern)


class Slate(DjangoModelFactory):
    class Meta:
        model = models.Slate
        # django_get_or_create = ("slug", )

    title = factory.Faker("title")
    creator = factory.SubFactory("accounts.factories.User",
            profile=factory.SubFactory("profiles.factories.Profile"))
    description = factory.Faker("text")


class SlateActionRelationship(DjangoModelFactory):
    class Meta:
        model = models.SlateActionRelationship

    slate = factory.SubFactory(Slate)
    action = factory.SubFactory("actions.factories.Action")
