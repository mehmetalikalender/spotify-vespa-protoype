from rest_framework import generics
from rest_framework.permissions import AllowAny
from django.contrib.auth import get_user_model
from .serializers import RegisterSerializer,UserSerializer
from rest_framework import generics, permissions

User = get_user_model()

class RegisterView(generics.CreateAPIView):
    """
    Yeni kullanıcı kaydı için API Ucu.
    Auth gerektirmez (AllowAny).
    """
    queryset = User.objects.all()
    permission_classes = (AllowAny,)
    serializer_class = RegisterSerializer

class ManageUserView(generics.RetrieveAPIView):
    """
    Giriş yapmış kullanıcının kendi bilgilerini (id, username, is_staff) getirir.
    Sadece giriş yapmış (Token sahibi) kullanıcılar erişebilir.
    """
    serializer_class = UserSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_object(self):
        # URL'den ID parametresi almak yerine, direkt isteği yapan kullanıcıyı döner.
        return self.request.user