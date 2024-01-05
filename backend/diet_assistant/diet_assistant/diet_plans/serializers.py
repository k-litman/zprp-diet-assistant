from rest_framework import serializers

from diet_assistant.diet_plans.models import Ingredient, Meal


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = ("id", "name")


class MealSerializer(serializers.ModelSerializer):
    ingredients = IngredientSerializer(many=True, read_only=True)

    class Meta:
        model = Meal
        fields = [
            "name",
            "description",
            "calories",
            "cuisine_type",
            "veganity",
            "ingredients",
        ]


class DayMealSerializer(serializers.Serializer):
    meal_type = serializers.CharField(max_length=20)
    meal = MealSerializer()


class DaySerializer(serializers.Serializer):
    day_number = serializers.IntegerField()
    meals = DayMealSerializer(many=True)


class DietPlanSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=100)
    days = DaySerializer(many=True)


class DietPlanCreateSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=100)
    days = serializers.IntegerField(max_value=31)
    meals_per_day = serializers.IntegerField(max_value=5)
    cuisine_type = serializers.CharField(max_length=20)
    veganity = serializers.DictField(child=serializers.BooleanField(default=False))
    restricted_ingredients = serializers.ListField(
        child=serializers.CharField(max_length=100)
    )  # Maybe pass ids?
    calories = serializers.IntegerField(min_value=0)
