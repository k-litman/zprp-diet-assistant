import json

from dataclasses import asdict, dataclass

from diet_assistant.diet_plans.choices import DietPlanStatus, MealType
from diet_assistant.diet_plans.models import Day, DayMeal, DietPlan, Meal
from diet_assistant.taskapp.celery import app


@dataclass
class CreateDietPlanCeleryTaskData:
    plan_id: int
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


@app.task(bind=True)
def create_diet_plan(self, data):
    data = CreateDietPlanCeleryTaskData.from_json(data)
    try:
        diet_plan = DietPlan.objects.get(id=data.plan_id)
    except DietPlan.DoesNotExist:
        self.retry(countdown=5)

    Day.objects.bulk_create(
        [
            Day(diet_plan=diet_plan, day_number=day_number)
            for day_number in range(1, data.days + 1)
        ]
    )

    possible_meals = Meal.objects.exclude(
        ingredients__name__in=data.restricted_ingredients
    )
    if data.cuisine_type and data.cuisine_type != "any":
        possible_meals = possible_meals.filter(cuisine_type=data.cuisine_type)

    for key, value in data.veganity.items():
        if value:
            possible_meals = possible_meals.filter(veganity=key)
        else:
            possible_meals = possible_meals.exclude(veganity=key)

    match data.meals_per_day:
        case 3:
            meals = [MealType.BREAKFAST, MealType.LUNCH, MealType.DINNER]
            calories_per_meal = [
                data.calories * 0.2,
                data.calories * 0.4,
                data.calories * 0.4,
            ]
        case 4:
            meals = [
                MealType.BREAKFAST,
                MealType.SNACK,
                MealType.LUNCH,
                MealType.DINNER,
            ]
            calories_per_meal = [
                data.calories * 0.2,
                data.calories * 0.2,
                data.calories * 0.4,
                data.calories * 0.2,
            ]
        case 5:
            meals = [
                MealType.BREAKFAST,
                MealType.SNACK,
                MealType.LUNCH,
                MealType.DESSERT,
                MealType.DINNER,
            ]
            calories_per_meal = [
                data.calories * 0.2,
                data.calories * 0.2,
                data.calories * 0.4,
                data.calories * 0.1,
                data.calories * 0.1,
            ]
        case _:
            diet_plan.error_message = "Invalid number of meals per day"
            diet_plan.status = DietPlanStatus.FAILED
            diet_plan.save()
            return

    for day in diet_plan.days.all():
        for meal_type, calories in zip(meals, calories_per_meal):
            meal = (
                possible_meals.filter(
                    calories__gte=calories * 0.9, calories__lte=calories * 1.1
                )
                .exclude(id__in=day.meals.all().values_list("meal_id", flat=True))
                .order_by("?")
                .first()
            )
            if meal is None:
                diet_plan.error_message = "Not enough meals to generate diet plan"
                diet_plan.status = DietPlanStatus.FAILED
                diet_plan.save()
                return
            DayMeal.objects.create(day=day, meal=meal, meal_type=meal_type)

    diet_plan.status = DietPlanStatus.GENERATED
    diet_plan.save()
