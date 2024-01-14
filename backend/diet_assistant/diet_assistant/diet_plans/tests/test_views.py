from unittest.mock import patch

from django.urls import reverse

import pytest

from rest_framework import status
from rest_framework.test import APIClient

from ...users.tests.factories import UserFactory
from ..tasks import CreateDietPlanCeleryTaskData
from .factories import (
    DayFactory,
    DayMealFactory,
    DietPlanFactory,
    IngredientFactory,
    MealFactory,
)


@pytest.mark.django_db
class TestMealViewSet:
    def test_list_meals(self):
        MealFactory.create_batch(5)
        client = APIClient()
        url = reverse("meals-list")
        response = client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert response.data["count"] == 5


@pytest.mark.django_db
class TestMyDietPlansViewSet:
    @patch("diet_assistant.diet_plans.tasks.create_diet_plan.delay")
    def test_create_diet_plan(self, mock_create_diet_plan):
        user = UserFactory()
        client = APIClient()
        client.force_authenticate(user=user)
        url = reverse("diet-plans-list")
        data = {
            "name": "Test Diet Plan",
            "days": 7,
            "meals_per_day": 3,
            "cuisine_type": "Italian",
            "veganity": {},
            "restricted_ingredients": [],
            "calories": 2000,
        }
        response = client.post(url, data, format="json")
        mock_create_diet_plan.assert_called_once()
        create_diet_plan_argument = CreateDietPlanCeleryTaskData.from_json(
            mock_create_diet_plan.call_args[0][0]
        )
        assert create_diet_plan_argument.plan_id == 1
        assert create_diet_plan_argument.days == data["days"]
        assert create_diet_plan_argument.meals_per_day == data["meals_per_day"]
        assert create_diet_plan_argument.cuisine_type == data["cuisine_type"]
        assert create_diet_plan_argument.veganity == data["veganity"]
        assert (
            create_diet_plan_argument.restricted_ingredients
            == data["restricted_ingredients"]
        )
        assert create_diet_plan_argument.calories == data["calories"]

        assert response.status_code == status.HTTP_200_OK


@pytest.mark.django_db
class TestIngredientsViewSet:
    def test_filter_ingredients(self):
        IngredientFactory(name="Apple")
        IngredientFactory(name="Banana")
        client = APIClient()
        url = reverse("ingredients-list") + "?name=apple"
        response = client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data["results"]) == 1
        assert response.data["results"][0]["name"] == "Apple"


@pytest.mark.django_db
class TestReplaceMealView:
    def test_replace_meal(self):
        user = UserFactory()
        diet_plan = DietPlanFactory(user=user)
        day = DayFactory(diet_plan=diet_plan)
        old_meal = MealFactory()
        new_meal = MealFactory()
        day_meal = DayMealFactory(day=day, meal=old_meal)

        client = APIClient()
        client.force_authenticate(user=user)

        url = reverse(
            "replace-meal",
            kwargs={
                "diet_plan_id": diet_plan.id,
                "day_id": day.id,
                "day_meal_id": day_meal.id,
            },
        )
        data = {"id": new_meal.id}

        response = client.patch(url, data, format="json")
        assert response.status_code == status.HTTP_204_NO_CONTENT

        day_meal = DayMealFactory._meta.model.objects.get(day=day, meal=new_meal)
        assert day_meal.meal.id == new_meal.id
