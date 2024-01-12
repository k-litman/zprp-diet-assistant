from rest_framework import status, viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from diet_assistant.diet_plans.models import DietPlan, Ingredient, Meal
from diet_assistant.diet_plans.serializers import (
    DietPlanCreateSerializer,
    DietPlanSerializer,
    IngredientSerializer,
    MealSerializer,
)

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

        # You can now use the validated data
        data = post_serializer.validated_data

        # Trigger your Celery task
        create_diet_plan.delay(
            CreateDietPlanCeleryTaskData(
                user_id=request.user.id,
                name=data["name"],
                days=data["days"],
                meals_per_day=data["meals_per_day"],
                cuisine_type=data["cuisine_type"],
                veganity=data["veganity"],
                restricted_ingredients=data["restricted_ingredients"],
                calories=data["calories"],
            ).to_json()
        )

        # You might want to use your main serializer here for the response
        headers = self.get_success_headers({})
        return Response({}, status=status.HTTP_200_OK, headers=headers)


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
