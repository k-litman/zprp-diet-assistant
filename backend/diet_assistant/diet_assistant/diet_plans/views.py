from rest_framework import status, viewsets
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from diet_assistant.diet_plans.models import DietPlan, Ingredient, Meal
from diet_assistant.diet_plans.serializers import (
    DietPlanCreateSerializer,
    DietPlanSerializer,
    IngredientSerializer,
    MealSerializer,
    ReplaceMealSerializer,
)

from .models import DayMeal
from .tasks import CreateDietPlanCeleryTaskData, create_diet_plan


class MealViewSet(viewsets.ReadOnlyModelViewSet):
    authentication_classes = []
    permission_classes = []
    queryset = Meal.objects.all()
    basename = "meals"
    serializer_class = MealSerializer


class MyDietPlansViewSet(viewsets.ModelViewSet):
    basename = "dietplan"
    serializer_class = DietPlanSerializer
    permission_classes = [IsAuthenticated]

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.user != request.user:
            return Response(status=status.HTTP_403_FORBIDDEN)
        serializer = DietPlanSerializer(instance)
        return Response(serializer.data)

    def get_queryset(self):
        return DietPlan.objects.filter(user=self.request.user)

    def create(self, request, *args, **kwargs):
        post_serializer = DietPlanCreateSerializer(data=request.data)
        post_serializer.is_valid(raise_exception=True)

        data = post_serializer.validated_data

        plan = DietPlan.objects.create(
            user=request.user,
            name=data["name"],
        )
        plan.save()

        create_diet_plan.delay(
            CreateDietPlanCeleryTaskData(
                plan_id=plan.id,
                days=data["days"],
                meals_per_day=data["meals_per_day"],
                cuisine_type=data["cuisine_type"],
                veganity=data["veganity"],
                restricted_ingredients=data["restricted_ingredients"],
                calories=data["calories"],
            ).to_json()
        )

        headers = self.get_success_headers({})
        serializer = DietPlanSerializer(plan)
        return Response(serializer.data, status=status.HTTP_200_OK, headers=headers)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.user != request.user and not request.user.is_superuser:
            return Response(status=status.HTTP_403_FORBIDDEN)
        self.perform_destroy(instance)

        return Response(status=status.HTTP_204_NO_CONTENT)


class IngredientsViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = IngredientSerializer
    basename = "ingredients"
    authentication_classes = []
    permission_classes = []

    def get_queryset(self):
        queryset = Ingredient.objects.all()
        name = self.request.query_params.get("name", None)
        if name is not None:
            queryset = queryset.filter(name__icontains=name)
        return queryset


class ReplaceMealView(APIView):
    def patch(self, request, diet_plan_id, day_id, day_meal_id):
        if get_object_or_404(DietPlan, id=diet_plan_id).user != request.user:
            return Response(status=status.HTTP_403_FORBIDDEN)

        day_meal = get_object_or_404(DayMeal, day_id=day_id, id=day_meal_id)
        serializer = ReplaceMealSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        new_meal = get_object_or_404(Meal, id=serializer.validated_data["id"])
        day_meal.meal = new_meal
        day_meal.save()

        return Response(status=status.HTTP_204_NO_CONTENT)
