from django.urls import include, path

from rest_framework import routers
from rest_framework.authtoken import views as drf_views

from diet_assistant.users import views

app_name = "users"

router = routers.DefaultRouter()
router.register("", views.UserViewSet)
urlpatterns = [
    path("login/", drf_views.obtain_auth_token),
    path("logout/", views.LogoutView.as_view(), name="logout"),
    path("", include(router.urls)),
]
