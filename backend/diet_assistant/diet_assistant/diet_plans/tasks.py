import json

from dataclasses import asdict, dataclass

from celery import shared_task

from diet_assistant.diet_plans.choices import DietPlanStatus, MealType
from diet_assistant.diet_plans.models import Day, DayMeal, DietPlan, Meal


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


@shared_task
def create_diet_plan(data):
    data = CreateDietPlanCeleryTaskData.from_json(data)
    diet_plan = DietPlan.objects.get(id=data.plan_id)

    Day.objects.bulk_create(
        [
            Day(diet_plan=diet_plan, day_number=day_number)
            for day_number in range(1, data.days + 1)
        ]
    )

    possible_meals = Meal.objects.filter(
        cuisine_type=data.cuisine_type, veganity=data.veganity
    ).exclude(ingredients__name__in=data.restricted_ingredients)

    # group meals in 'days' packs of 'meals_per_day', as close to desired calories as possible
    calories_per_meal = data.calories / data.meals_per_day

    match data.meals_per_day:
        case 3:
            meals = [MealType.BREAKFAST, MealType.LUNCH, MealType.DINNER]
            calories_per_meal = [
                calories_per_meal * 0.2,
                calories_per_meal * 0.4,
                calories_per_meal * 0.4,
            ]
        case 4:
            meals = [
                MealType.BREAKFAST,
                MealType.SNACK,
                MealType.LUNCH,
                MealType.DINNER,
            ]
            calories_per_meal = [
                calories_per_meal * 0.2,
                calories_per_meal * 0.2,
                calories_per_meal * 0.4,
                calories_per_meal * 0.2,
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
                calories_per_meal * 0.2,
                calories_per_meal * 0.2,
                calories_per_meal * 0.4,
                calories_per_meal * 0.1,
                calories_per_meal * 0.1,
            ]
        case _:
            diet_plan.error_message = "Invalid number of meals per day"
            diet_plan.status = DietPlanStatus.FAILED
            diet_plan.save()
            return

    for day in diet_plan.days.all():
        for meal_type, calories, order in zip(
            meals, calories_per_meal, range(1, data.meals_per_day + 1)
        ):
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
            DayMeal.objects.create(day=day, meal=meal, meal_type=meal_type, order=order)

    diet_plan.status = DietPlanStatus.GENERATED
    diet_plan.save()
