from django.contrib.auth import get_user_model

from rest_framework import permissions, status, viewsets
from rest_framework.response import Response
from rest_framework.views import APIView

from diet_assistant.users.serializers import UserSerializer

User = get_user_model()


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def get_permissions(self):
        if self.request.method == "POST":
            # Allow any access for POST requests
            return [permissions.AllowAny()]
        else:
            # For other methods, use the default permission set
            # Example: permissions.IsAuthenticated()
            return [permissions.IsAuthenticated()]


class LogoutView(APIView):
    def delete(self, request):
        request.auth.delete()
        return Response({}, status=status.HTTP_204_NO_CONTENT)
