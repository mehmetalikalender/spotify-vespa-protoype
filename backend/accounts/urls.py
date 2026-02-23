from django.urls import path
from .views import RegisterView,ManageUserView
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

urlpatterns = [
    # Kayıt Ol
    path('register/', RegisterView.as_view(), name='register'),
    
    # Giriş Yap (Token Al) -> Access + Refresh Token döner
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    
    # Token Yenile (Access Token süresi bitince Refresh Token ile yenisini al)
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    # Kullanıcı Detayları (Ben Kimim?)
    path('me/', ManageUserView.as_view(), name='me'),
]