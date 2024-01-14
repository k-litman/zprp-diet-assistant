from django.urls import path

from rest_framework import routers

from diet_assistant.diet_plans import views

meals_path = "meals"
diet_plans_path = "diet-plans"
ingredients_path = "ingredients"
replace_meal_path = f"{diet_plans_path}/<int:diet_plan_id>/day/<int:day_id>/meal/<int:day_meal_id>/replace/"

router = routers.DefaultRouter()
router.register(meals_path, views.MealViewSet, basename=meals_path)
router.register(diet_plans_path, views.MyDietPlansViewSet, basename=diet_plans_path)
router.register(ingredients_path, views.IngredientsViewSet, basename=ingredients_path)

urlpatterns = router.urls + [
    path(replace_meal_path, views.ReplaceMealView.as_view(), name="replace-meal")
]
