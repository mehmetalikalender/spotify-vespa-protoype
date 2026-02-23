# music/admin.py
from django.contrib import admin
from django.utils.html import format_html
from .models import Song, Playlist


@admin.register(Song)
class SongAdmin(admin.ModelAdmin):
    list_display = ("title", "artist", "audio_preview", "duration_seconds", "created_at")
    search_fields = ("title", "artist")
    list_filter = ("artist",)
    ordering = ("-created_at",)
    readonly_fields = ("created_at", "audio_preview")
    # çok şarkı olunca performans için sayfalama default zaten var

    def audio_preview(self, obj):
        """Admin’de küçük bir audio player göster (dosya varsa)."""
        if obj.audio_file:
            return format_html(
                '<audio controls style="height:28px; width:260px;">'
                '<source src="{}" type="audio/mpeg">Tarayıcınız ses çalmayı desteklemiyor.'
                '</audio>',
                obj.audio_file.url
            )
        return "-"

    audio_preview.short_description = "Önizleme"


@admin.register(Playlist)
class PlaylistAdmin(admin.ModelAdmin):
    list_display = ("name", "owner", "is_public", "song_count", "created_at")
    list_filter = ("is_public",)
    search_fields = ("name", "owner__username", "owner__email")
    ordering = ("-created_at",)
    readonly_fields = ("created_at", "updated_at")

    # çok-çok seçim için kullanışlı bir UI
    filter_horizontal = ("songs",)

    # çok büyük veri setlerinde daha performanslı arama için açılabilir:
    # autocomplete_fields = ("owner", "songs",)

    def song_count(self, obj):
        return obj.songs.count()
    song_count.short_description = "Şarkı Sayısı"
