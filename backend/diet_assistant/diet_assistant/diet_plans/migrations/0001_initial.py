# Generated by Django 4.1.13 on 2023-12-05 20:09

import django.db.models.deletion

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="Day",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("day_number", models.IntegerField()),
            ],
        ),
        migrations.CreateModel(
            name="Ingredient",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("name", models.CharField(db_index=True, max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name="Meal",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("name", models.CharField(max_length=100)),
                ("description", models.TextField()),
                ("calories", models.IntegerField()),
                (
                    "cuisine_type",
                    models.CharField(
                        choices=[
                            ("it", "Italian"),
                            ("pl", "Polish"),
                            ("fr", "French"),
                            ("mx", "Mexican"),
                            ("as", "Asian"),
                        ],
                        max_length=20,
                    ),
                ),
                (
                    "veganity",
                    models.CharField(
                        choices=[
                            ("vegan", "Vegan"),
                            ("vegetarian", "Vegetarian"),
                            ("meat", "Meat"),
                            ("fish", "Fish"),
                        ],
                        max_length=20,
                    ),
                ),
                (
                    "ingredients",
                    models.ManyToManyField(
                        related_name="meals", to="diet_plans.ingredient"
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="DietPlan",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("name", models.CharField(max_length=100)),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="diet_plans",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="DayMeal",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "meal_type",
                    models.CharField(
                        choices=[
                            ("breakfast", "Breakfast"),
                            ("lunch", "Lunch"),
                            ("dinner", "Dinner"),
                            ("snack", "Snack"),
                            ("dessert", "Dessert"),
                        ],
                        max_length=20,
                    ),
                ),
                (
                    "day",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="meals",
                        to="diet_plans.day",
                    ),
                ),
                (
                    "meal",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="diet_plans.meal",
                    ),
                ),
            ],
        ),
        migrations.AddField(
            model_name="day",
            name="diet_plan",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="days",
                to="diet_plans.dietplan",
            ),
        ),
    ]
