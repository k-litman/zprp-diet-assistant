import random
import time

import locust.exception
from locust import HttpUser, task, events, run_single_user, between
from faker import Faker
from time import sleep
fake = Faker()

DEBUG = False


def log(*args, **kwargs):
    if DEBUG:
        return print(*args, **kwargs)


class CreateDietPlan(HttpUser):
    wait_time = between(1, 5)
    host = "http://0.0.0.0:8000"
    user_id = None

    def create_user(self):
        self.user_id = random.randint(0, 1000000)
        self.client.post(
            "/users/",
            json={
                "username": f"test_user_{self.user_id}",
                "password": "test_password",
            },
        )

    def login(self):
        response = self.client.post(
            "/users/login/",
            json={
                "username": f"test_user_{self.user_id}",
                "password": "test_password",
            },
        )
        self.client.headers["Authorization"] = f"Bearer {response.json()['token']}"

    def logout(self):
        self.client.delete("/users/logout/")

    def on_start(self):
        self.create_user()
        self.login()

    @task
    def create_diet_plan(self):
        self.client.post(
            "/diets/diet-plan/",
            json={
                "name": fake.name(),
                "days": 7,
                "meals_per_day": 3,
                "cuisine_type": "italian",
                "veganity": {
                    "vegan": True
                },
                "restricted_ingredients": [
                    "Ingredient 1"
                ],
                "calories": 100
            }
        )

    @task
    def get_diet_plans(self):
        self.client.get("/diets/diet-plan/")

    @task
    def get_meals(self):
        self.client.get("/diets/meal/")

    @task
    def get_ingredients(self):
        self.client.get("/diets/ingredient/")


    # @task
    # def e2e(self):
    #     initial_count = self.client.get("/diets/diet-plans/").json()["count"]
    #     self.client.post(
    #         "/diets/diet-plans/",
    #         json={
    #             "name": "MY_diet_plan",
    #             "days": 7,
    #             "meals_per_day": 3,
    #             "cuisine_type": "italian",
    #             "veganity": {
    #                 "vegan": True
    #             },
    #             "restricted_ingredients": [
    #                 "Ingredient 1"
    #             ],
    #             "calories": 100
    #         }
    #     )
    #     last_count = initial_count
    #     while last_count == initial_count:
    #         last_count = self.client.get("/diets/diet-plans/").json()["count"]
    #
    #     self.client.get("/diets/meals/")


if __name__ == "__main__":
    run_single_user(CreateDietPlan)
