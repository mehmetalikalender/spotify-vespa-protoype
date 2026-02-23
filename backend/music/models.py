from django.db import models
from django.conf import settings

class Song(models.Model):
  

    title = models.CharField(max_length=255, verbose_name="Şarkı Adı")
    artist = models.CharField(max_length=255, verbose_name="Sanatçı")
    
    # seaweedFs entegrasyonu 
    seaweed_file_id = models.CharField(max_length=255, unique=True, verbose_name="SeaweedFS File ID")
    # seaweedFs tarafından atanan unique dosya kimliği; içerisinde dosyanın volume içindeki yeri ile ilgili veriler barındırır

    stream_url = models.URLField(max_length=1000, verbose_name="Streaming URL") 
    #Dosyanın bulunduğu volume suncuusunun http adresi frontend doğrudan bu adresten dosyayı çeker

    # Oluşturma tarihi / şarkı süresi
    duration_seconds = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    # Vespa entegrasyonu için genre ve poplarity alanları eklendi.
    genre = models.CharField(max_length=100, blank=True, null=True, verbose_name="Tür")
    popularity = models.PositiveIntegerField(default=0, verbose_name="Popülerlik Skoru")

    def __str__(self):
        return f"{self.artist} - {self.title}"

#Playlist modeli
class Playlist(models.Model):

    #Kullanıcı <one to many ilişkisi> Playlist 
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='playlists')
    name = models.CharField(max_length=255)
    is_public = models.BooleanField(default=False)
    songs = models.ManyToManyField(Song, related_name='playlists', blank=True) #Song Playlist many to many
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} - {self.owner.username}"