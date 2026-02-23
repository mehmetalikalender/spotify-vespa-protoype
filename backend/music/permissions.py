
from rest_framework.permissions import BasePermission 
# DRF'ten BasePermission'ı import etmeyi unutmayın

class IsOwner(BasePermission):
    message = "Bu playlist üzerinde yetkiniz yok."
    
    # has_object_permission metodu KRİTİK. 
    # obj'nin sahibinin, isteği yapan kullanıcı olup olmadığını kontrol eder.
    def has_object_permission(self, request, view, obj):
        # Güvenli metotlara (GET, HEAD, OPTIONS) genellikle burada izin verilebilir, 
        # ama sizin mantığınız sadece sahibi için GET'i de kontrol ediyor.
        
        # Obje üzerindeki 'owner_id' alanı ile isteği yapan kullanıcının ID'si eşit mi?
        return getattr(obj, "owner_id", None) == request.user.id