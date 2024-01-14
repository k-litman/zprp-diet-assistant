import os
import time

from unittest.mock import patch

from django.test import TestCase

from rest_framework import status
from rest_framework.response import Response
from rest_framework.test import APIClient

from diet_assistant.diet_plans.tasks import CreateDietPlanCeleryTaskData

script_dir = os.path.dirname(os.path.abspath(__file__))
fixtures_path = os.path.join(script_dir, "fixture.json")


class CreateUserTest(TestCase):
    def setUp(self) -> None:
        self.client: APIClient = APIClient()

    def test_valid_user_created(self) -> None:
        response: Response = create_account(self.client)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["username"], "test")

    def test_unique_username_required(self) -> None:
        create_account(self.client)
        response: Response = create_account(self.client)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data["detail"]["username"],
            ["A user with that username already exists."],
        )

    def test_password_required(self) -> None:
        response: Response = create_account(self.client, "test", "")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data["detail"]["password"], ["This field may not be blank."]
        )

    def test_username_required(self) -> None:
        response: Response = create_account(self.client, "", "test")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data["detail"]["username"], ["This field may not be blank."]
        )


class DietPlanTest(TestCase):
    fixtures = [fixtures_path]

    def setUp(self) -> None:
        self.client: APIClient = APIClient()
        self.user: Response = create_account(self.client)
        token_response: Response = login(self.client)
        self.client.credentials(
            HTTP_AUTHORIZATION="Bearer " + token_response.data["token"]
        )

    def create_diet_plan(self, name: str) -> Response:
        return self.client.post(
            "/diets/diet-plans/",
            data={
                "name": name,
                "days": 7,
                "meals_per_day": 3,
                "cuisine_type": "italian",
                "veganity": {"vegan": True},
                "restricted_ingredients": [],
                "calories": 2000,
            },
            format="json",
        )

    @patch("diet_assistant.diet_plans.tasks.create_diet_plan.delay")
    def test_create_diet_plan(self, mock_task):
        # Make a request to the endpoint
        response = self.create_diet_plan("test")
        self.assertEqual(response.status_code, 200)

        self.assertEqual(response.data["name"], "test")
        self.assertEqual(response.data["generated"], False)

        # Verify that the Celery task was called
        mock_task.assert_called_once_with(
            CreateDietPlanCeleryTaskData(
                plan_id=response.data["id"],
                days=7,
                meals_per_day=3,
                cuisine_type="italian",
                veganity={"vegan": True},
                restricted_ingredients=[],
                calories=2000,
            ).to_json()
        )


class E2ETest(TestCase):
    fixtures = [fixtures_path]

    def setUp(self) -> None:
        self.client: APIClient = APIClient()

    def test_end_to_end(self):
        create_account(self.client)

        token_response = login(self.client)
        self.assertEqual(token_response.status_code, 200)

        self.client.credentials(
            HTTP_AUTHORIZATION="Bearer " + token_response.data["token"]
        )

        ingredient_response = self.client.get("/diets/ingredients/?name=pasta")
        restricted_ingredient = ingredient_response.data["results"][0]["id"]

        diet_plan_response = self.client.post(
            "/diets/diet-plans/",
            data={
                "name": "E2E Test",
                "days": 7,
                "meals_per_day": 3,
                "cuisine_type": "italian",
                "veganity": {"vegan": True},
                "restricted_ingredients": [restricted_ingredient],
                "calories": 2000,
            },
            format="json",
        )

        self.assertEqual(diet_plan_response.status_code, 200)
        self.assertEqual(diet_plan_response.data["name"], "E2E Test")
        self.assertEqual(diet_plan_response.data["generated"], False)

        while not diet_plan_response.data["generated"]:
            diet_plan_response = self.client.get(
                f"/diets/diet-plans/{diet_plan_response.data['id']}/"
            )
            self.assertEqual(diet_plan_response.status_code, 200)
            time.sleep(3)

        self.assertEqual(diet_plan_response.data["generated"], True)
        self.assertEqual(len(diet_plan_response.data["days"]), 7)
        # TODO Uncomment after fixing the algorithm
        # for day in diet_plan_response.data['days']:
        #     # self.assertEqual(len(day), 3)
        #     for meal in day['meals']:
        #         self.assertEqual(meal['cuisine_type'], 'italian')
        #         self.assertEqual(meal['veganity'], 'vegan')
        #         self.assertNotIn(restricted_ingredient, meal['ingredients'])

        meal_response = self.client.get("/diets/meals/")
        self.assertEqual(meal_response.status_code, 200)
        diet_plan_id = diet_plan_response.data["id"]
        day_id = diet_plan_response.data["days"][0]["id"]
        meal_id = diet_plan_response.data["days"][0]["meals"][0]["id"]

        new_meal = None
        for meal in meal_response.data["results"]:
            if (
                meal["id"]
                != diet_plan_response.data["days"][0]["meals"][0]["meal"]["id"]
            ):
                new_meal = meal
                break

        replace_meal_response = self.client.patch(
            f"/diets/diet-plans/{diet_plan_id}/day/{day_id}/meal/{meal_id}/replace/",
            data={"id": new_meal["id"]},
        )

        self.assertEqual(replace_meal_response.status_code, 204)
        diet_plan_response = self.client.get(
            f"/diets/diet-plans/{diet_plan_response.data['id']}/"
        )
        self.assertEqual(diet_plan_response.status_code, 200)
        self.assertEqual(
            diet_plan_response.data["days"][0]["meals"][0]["meal"]["id"], new_meal["id"]
        )


def create_account(
    client: APIClient, username: str = "test", password: str = "test"
) -> Response:
    return client.post("/users/", data={"username": username, "password": password})


def login(
    client: APIClient, username: str = "test", password: str = "test"
) -> Response:
    return client.post(
        "/users/login/", data={"username": username, "password": password}
    )
