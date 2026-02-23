from rest_framework import serializers
from .models import Song, Playlist

class SongSerializer(serializers.ModelSerializer):
    # Frontend'den dosya almak için 'write_only' (sadece yazılabilir) bir alan ekliyoruz.
    # Bu alan veritabanında YOK, sadece veri transferi için var.
    audio_file = serializers.FileField(write_only=True, required=True)

    class Meta:
        model = Song
        # 'audio_file' gönderilir, 'seaweed_file_id' ve 'stream_url' okunur.
        fields = ("id", "title", "artist", "audio_file", "duration_seconds", "created_at", "seaweed_file_id", "stream_url")
        read_only_fields = ("id", "created_at", "seaweed_file_id", "stream_url")

    def create(self, validated_data):
        # Dosya buraya kadar geldiyse view tarafında işlenip modelden bağımsız yönetilecek.
        # Bu metodun çalışmasını beklemeden ViewSet içinde müdahale edeceğiz.
        # O yüzden burası standart kalabilir, asıl işi ViewSet yapacak.
        validated_data.pop('audio_file', None) # Dosyayı model create'e sokma, patlar.
        return super().create(validated_data)

class PlaylistReadSerializer(serializers.ModelSerializer):
    songs = SongSerializer(many=True, read_only=True)
    class Meta:
        model = Playlist
        fields = ("id", "name", "is_public", "songs", "created_at", "updated_at")
        read_only_fields = ("id", "created_at", "updated_at")

class PlaylistWriteSerializer(serializers.ModelSerializer):
    song_ids = serializers.ListField(child=serializers.IntegerField(min_value=1), required=False, write_only=True)
    class Meta:
        model = Playlist
        fields = ("id", "name", "is_public", "song_ids")
        read_only_fields = ("id",)
    
    def create(self, validated_data):
        song_ids = validated_data.pop("song_ids", [])
        playlist = Playlist.objects.create(owner=self.context["request"].user, **validated_data)
        if song_ids:
            songs = Song.objects.filter(id__in=song_ids)
            playlist.songs.set(songs)
        return playlist

    def update(self, instance, validated_data):
        song_ids = validated_data.pop("song_ids", None)
        instance.name = validated_data.get("name", instance.name)
        instance.is_public = validated_data.get("is_public", instance.is_public)
        instance.save()
        if song_ids is not None:
            songs = Song.objects.filter(id__in=song_ids)
            instance.songs.set(songs)
        return instance