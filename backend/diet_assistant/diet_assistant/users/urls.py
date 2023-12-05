from rest_framework import routers

from diet_assistant.users import views

app_name = "users"

router = routers.DefaultRouter()
router.register("", views.UserViewSet)
urlpatterns = router.urls
