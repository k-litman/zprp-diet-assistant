from rest_framework import routers

from diet_assistant.diet_plans import views

meals_path = "meals"
diet_plans_path = "diet-plans"
ingredients_path = "ingredients"

router = routers.DefaultRouter()
router.register(meals_path, views.MealViewSet, basename=meals_path)
router.register(diet_plans_path, views.MyDietPlansViewSet, basename=diet_plans_path)
router.register(ingredients_path, views.IngredientsViewSet, basename=ingredients_path)
urlpatterns = router.urls
