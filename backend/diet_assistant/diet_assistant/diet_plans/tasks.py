import json

from dataclasses import asdict, dataclass
from time import sleep
from typing import Dict, List

from celery import shared_task

from .models import Day, DayMeal, DietPlan, Ingredient, Meal


@dataclass
class CreateDietPlanCeleryTaskData:
    plan_id: int
    days: int
    meals_per_day: int
    cuisine_type: str
    veganity: Dict[str, bool]
    restricted_ingredients: List[str]
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
    data = CreateDietPlanCeleryTaskData.from_json(data)
    try:
        diet_plan = DietPlan.objects.get(id=data.plan_id)
        if diet_plan.generated:
            # TODO: Log error
            return data
        algorithm(
            days=data.days,
            meals_per_day=data.meals_per_day,
            cuisine_type=data.cuisine_type,
            veganity=data.veganity,
            restricted_ingredients=data.restricted_ingredients,
            diet_plan=diet_plan,
        )
    except DietPlan.DoesNotExist:
        create_diet_plan.retry(
            countdown=5, max_retries=3, kwargs={"data": data.to_json()}
        )
        return
    return


def algorithm(
    days: int,
    meals_per_day: int,
    cuisine_type: str,
    veganity: Dict[str, bool],
    restricted_ingredients: List[str],
    diet_plan: DietPlan,
):
    for i in range(1, 8):  # Assuming a 7-day diet plan
        Day.objects.create(diet_plan=diet_plan, day_number=i)

    # Create Ingredients (you can also fetch existing ingredients)
    ingredient1, _ = Ingredient.objects.get_or_create(name="Ingredient 1")
    ingredient2, _ = Ingredient.objects.get_or_create(name="Ingredient 2")

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
        sleep(2)
    DietPlan.objects.filter(id=diet_plan.id).update(generated=True)
