from django.db import models
from django.utils.translation import gettext_lazy as _


class MealType(models.TextChoices):
    BREAKFAST = "breakfast", _("Breakfast")
    LUNCH = "lunch", _("Lunch")
    DINNER = "dinner", _("Dinner")
    SNACK = "snack", _("Snack")
    DESSERT = "dessert", _("Dessert")


class CuisineType(models.TextChoices):
    ITALIAN = "it", _("Italian")
    POLISH = "pl", _("Polish")
    FRENCH = "fr", _("French")
    MEXICAN = "mx", _("Mexican")
    ASIAN = "as", _("Asian")
    SPANISH = "sp", _("Spanish")
    AMERICAN = "us", _("American")


class Veganity(models.TextChoices):
    VEGAN = "vegan", _("Vegan")
    VEGETARIAN = "vegetarian", _("Vegetarian")
    MEAT = "meat", _("Meat")
    FISH = "fish", _("Fish")
