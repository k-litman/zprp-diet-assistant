from django.contrib.auth import get_user_model
from django.db import models

from diet_assistant.diet_plans.choices import CuisineType, MealType, Veganity

User = get_user_model()


class Ingredient(models.Model):
    name = models.CharField(max_length=100, db_index=True)

    def __str__(self):
        return self.name


class DietPlan(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="diet_plans")
    name = models.CharField(max_length=100)
    generated = models.BooleanField(default=False)

    def __str__(self):
        return self.name


class Day(models.Model):
    diet_plan = models.ForeignKey(
        DietPlan, related_name="days", on_delete=models.CASCADE
    )
    day_number = models.IntegerField()

    def __str__(self):
        return f"Day {self.day_number} of {self.diet_plan.name}"


class Meal(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    calories = models.IntegerField()
    cuisine_type = models.CharField(max_length=20, choices=CuisineType.choices)
    veganity = models.CharField(max_length=20, choices=Veganity.choices)
    ingredients = models.ManyToManyField(Ingredient, related_name="meals")

    def __str__(self):
        return self.name


class DayMeal(models.Model):
    day = models.ForeignKey(Day, related_name="meals", on_delete=models.CASCADE)
    meal = models.ForeignKey(Meal, on_delete=models.CASCADE)
    meal_type = models.CharField(max_length=20, choices=MealType.choices)

    def __str__(self):
        return f"{self.meal.name} ({self.meal_type}) for {self.day}"
