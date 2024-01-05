import pytest

from diet_assistant.diet_plans.tests.factories import MealFactory


@pytest.fixture
def meals_factory():
    return MealFactory


@pytest.fixture
def meal_instance(meals_factory: MealFactory):
    return meals_factory.build()
