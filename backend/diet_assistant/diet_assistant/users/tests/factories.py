from django.conf import settings

import factory


class UserFactory(factory.django.DjangoModelFactory):
    username = factory.Sequence(lambda n: f"user-{n}")
    email = factory.Sequence(lambda n: f"user-{n}@example.com")

    @factory.post_generation
    def password(obj, create, extracted, **kwargs):
        if not extracted:
            extracted = "hunter2"
        obj.set_password(extracted)

    class Meta:
        model = settings.AUTH_USER_MODEL
        django_get_or_create = ("username",)
