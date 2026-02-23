from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import SongViewSet, PlaylistViewSet

from .views import get_recommendations

router = DefaultRouter() # DefaultRouter örneği oluştur
router.register(r'songs', SongViewSet, basename='song') #Otomatik olarak URL'leri oluştur
router.register(r'playlists', PlaylistViewSet, basename='playlist') #Otomatik olarak URL'leri oluştur

urlpatterns = [
    path('', include(router.urls)),
    path('recommendations/', get_recommendations, name='get_recommendations'),
]
