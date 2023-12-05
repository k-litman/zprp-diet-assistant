import pytest


class TestUser:
    def test_string_representation(self, user_instance):
        assert str(user_instance) == user_instance.username

    @pytest.mark.django_db
    def test_factory_default_password(self, user):
        assert user.has_usable_password()
