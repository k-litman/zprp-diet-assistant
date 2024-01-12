import json
from typing import List, Set, Dict
import django


def parse_json():
    with open('./initial_data.json') as json_file:
        return json.load(json_file)


def get_ingredients(data: List[Dict]) -> Set[str]:
    return set([ingredient for meal in data for ingredient in meal['ingredients']])


def populate_database(meals: List[Dict], ingredients: Set[str]):
    for ingredient in ingredients:
        Ingredient.objects.create(name=ingredient)
    for meal in meals:
        meal_ingredients = [Ingredient.objects.get(name=ingredient) for ingredient in meal['ingredients']]
        Meal.objects.create(
            name=meal['name'],
            description=meal['description'],
            calories=meal['calories'],
            cuisine_type=CuisineType[meal['cuisine_type'].upper()].value,
            veganity=Veganity[meal['veganity'].upper()].value,
        ).ingredients.set(meal_ingredients)


def clear_database():
    Meal.objects.all().delete()
    Ingredient.objects.all().delete()


def main():
    clear_database()
    data = parse_json()
    ingredients = get_ingredients(data)
    populate_database(data, ingredients)


if __name__ == '__main__':
    django.setup()
    from diet_assistant.diet_plans.models import Ingredient, Meal
    from diet_assistant.diet_plans.choices import CuisineType, Veganity
    main()
