from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # Yönetim Paneli
    path('admin/', admin.site.urls),
    
    # Auth İşlemleri (Login, Register, Token)
    path('api/accounts/', include('accounts.urls')),
    
    # Müzik İşlemleri (Şarkılar, Listeler)
    # Prefix 'api/music/' olarak değiştirildi
    path('api/music/', include('music.urls')),
]

# Development ortamında static/media dosyalarına erişim için (Debug=True ise)
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)