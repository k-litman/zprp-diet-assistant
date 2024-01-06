import json

from dataclasses import asdict, dataclass
from time import sleep

from celery import shared_task

from .models import Day, DayMeal, DietPlan, Ingredient, Meal, User


@dataclass
class CreateDietPlanCeleryTaskData:
    user_id: int
    name: str
    days: int
    meals_per_day: int
    cuisine_type: str
    veganity: dict[bool]
    restricted_ingredients: list[str]
    calories: int

    def to_dict(self):
        return asdict(self)

    @staticmethod
    def from_dict(data_dict):
        return CreateDietPlanCeleryTaskData(**data_dict)

    def to_json(self):
        return json.dumps(self.to_dict())

    @staticmethod
    def from_json(data_json):
        return CreateDietPlanCeleryTaskData.from_dict(json.loads(data_json))


@shared_task
def create_diet_plan(data):
    print(CreateDietPlanCeleryTaskData.from_json(data))
    # sleep for 10 seconds then create a meal plan
    user = User.objects.get(id=1)

    diet_plan = DietPlan.objects.create(user=user, name="Sample Diet Plan")
    # Create related Day instances
    for i in range(1, 8):  # Assuming a 7-day diet plan
        Day.objects.create(diet_plan=diet_plan, day_number=i)

    # Create Ingredients (you can also fetch existing ingredients)
    ingredient1 = Ingredient.objects.get_or_create(name="Ingredient 1")
    ingredient2 = Ingredient.objects.get_or_create(name="Ingredient 2")

    # Create Meal instances
    meal1, created = Meal.objects.get_or_create(
        name="Meal 1",
        description="Delicious meal 1 description",
        calories=500,
        cuisine_type="Italian",
        veganity="Vegan",
    )
    if created:
        meal1.ingredients.add(ingredient1, ingredient2)
    for day in diet_plan.days.all():
        DayMeal.objects.create(day=day, meal=meal1, meal_type="Breakfast")
    sleep(10)
    return data
