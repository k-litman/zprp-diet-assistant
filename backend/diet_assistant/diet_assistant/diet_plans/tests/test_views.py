from unittest.mock import patch

from django.urls import reverse

import pytest

from rest_framework import status
from rest_framework.test import APIClient

from ..tasks import CreateDietPlanCeleryTaskData
from .factories import IngredientFactory, MealFactory, UserFactory


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
        assert create_diet_plan_argument.user_id == user.id
        assert create_diet_plan_argument.name == data["name"]
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
