from rest_framework import viewsets, status,filters
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAdminUser
from rest_framework.decorators import action
from rest_framework.response import Response
from django.http import HttpResponseRedirect # Yönlendirme için gerekli

from django.http import JsonResponse
from .models import Song
from .services.vespa_service import VespaService
import random

from .models import Song, Playlist
from .serializers import SongSerializer, PlaylistReadSerializer, PlaylistWriteSerializer
# from .services import SeaweedFSService
from .services.services import SeaweedFSService

# Basit Permission Sınıfı
from rest_framework.permissions import BasePermission
class IsOwner(BasePermission):
    def has_object_permission(self, request, view, obj):
        if not hasattr(obj, 'owner'):
            return False
        return obj.owner == request.user


class SongViewSet(viewsets.ModelViewSet):
    queryset = Song.objects.all().order_by("-created_at")
    serializer_class = SongSerializer

    filter_backends = [filters.SearchFilter]
    search_fields = ['title', 'artist']

    def get_permissions(self):
        # Şarkı listesini ve stream işlemini herkes yapabilir
        if self.action in ["list", "retrieve", "stream"]:
            return [AllowAny()]
        return [IsAdminUser()]

    def perform_create(self, serializer):
        """Dosyayı SeaweedFS'e yükler"""
        uploaded_file = self.request.FILES.get('audio_file') # Dosyayı request den çek
        if not uploaded_file:
            raise Exception("Ses dosyası gerekli!")

        try:
            fid, stream_url = SeaweedFSService.upload_file(uploaded_file) # SeaweedFSService dosyayı gönder, fId ve streamUrl döner
        except Exception as e:
            print(f"SeaweedFS Upload Hatası: {e}")
            raise e

        serializer.save(seaweed_file_id=fid, stream_url=stream_url) #Veri tabanına yazarken fid ve url ekle


    # stream enpoointi 
    @action(detail=True, methods=['get'])
    def stream(self, request, pk=None):
        """
        Kullanıcıyı dinamik olarak doğru Volume sunucusuna yönlendirir.
        """
        song = self.get_object()
        
        file_id = song.seaweed_file_id
        
        # bu sservis bize http://localhost:8081/3,abc  gibi çalışan bir link dönecek
        final_url = SeaweedFSService.get_file_url(file_id)
        
        # Eğer adres bulunamadıysa veya servis hata verdiyse
        if not final_url:
            final_url = song.stream_url

        return HttpResponseRedirect(final_url) # İsteği atanı doğrudan kaynağa yönlendirir
    


class PlaylistViewSet(viewsets.ModelViewSet):
    
    def get_queryset(self):
        return Playlist.objects.filter(owner=self.request.user).order_by("-created_at")

    def get_permissions(self):
        return [IsAuthenticated(), IsOwner()]

    def get_serializer_class(self):
        if self.action in ["create", "update", "partial_update"]:
            return PlaylistWriteSerializer
        return PlaylistReadSerializer

    @action(detail=True, methods=["post"], url_path="add-song")
    def add_song(self, request, pk=None):
        playlist = self.get_object()
        song_id = request.data.get("song_id")
        if not song_id:
            return Response({"detail": "song_id gerekli"}, status=status.HTTP_400_BAD_REQUEST)
        try:
            song = Song.objects.get(pk=song_id)
            playlist.songs.add(song)
            return Response({"detail": "Şarkı eklendi"}, status=status.HTTP_200_OK)
        except Song.DoesNotExist:
            return Response({"detail": "Şarkı bulunamadı"}, status=status.HTTP_404_NOT_FOUND)

    @action(detail=True, methods=["post"], url_path="remove-song")
    def remove_song(self, request, pk=None):
        playlist = self.get_object()
        song_id = request.data.get("song_id")
        if not song_id:
            return Response({"detail": "song_id gerekli"}, status=status.HTTP_400_BAD_REQUEST)
        try:
            song = Song.objects.get(pk=song_id)
            playlist.songs.remove(song)
            return Response({"detail": "Şarkı çıkarıldı"}, status=status.HTTP_200_OK)
        except Song.DoesNotExist:
            return Response({"detail": "Şarkı bulunamadı"}, status=status.HTTP_404_NOT_FOUND)
        
def get_recommendations(request):
    #  URLden stratejiyi al ?strategy=hybrid_ranking veya similarity_ranking
    strategy = request.GET.get('strategy', 'similarity_ranking')
    
    # Kullanıcı Profilini Al mock embedding 3 boyutlu rastgele bir vektör üretilir
    mock_user_vector = [random.random(), random.random(), random.random()]
    
    # Vespa ya sor retrieval - ranking
    vespa = VespaService()
    vespa_results = vespa.recommend(mock_user_vector, strategy=strategy)
    
    if not vespa_results:
        return JsonResponse({"error": "Vespa error"}, status=500)
 
    # Vespa dan gelen şarkı Id lerini topla
    hits = vespa_results.get('root', {}).get('children', [])
    song_ids = [hit['fields']['song_id'] for hit in hits if 'fields' in hit]
    
    # SQLite tan güncel detayları çek şarkı detaylarını çek 
    songs = Song.objects.filter(id__in=song_ids)
    
    # Sonuçları JSON olarak dön
    results = []
    for hit in hits:
        s_id = hit['fields']['song_id']
        song_obj = next((s for s in songs if s.id == s_id), None)
        if song_obj:
            results.append({
                "id": song_obj.id,
                "title": song_obj.title,
                "artist": song_obj.artist,
                "url": song_obj.stream_url,
                "score": hit['relevance'], # Vespa nın verdiği başarı puanı
                "genre": hit['fields'].get('genre'),
                "popularity": hit['fields'].get('popularity'), # Vespa'dan gelen popülerlik
                "embedding": hit['fields'].get('embedding')  # Vespa'dan gelen vektör
            })

    return JsonResponse({
        "strategy_used": strategy,
        "user_vector": mock_user_vector,
        "recommendations": results
    })