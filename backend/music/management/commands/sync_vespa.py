import json
import random
import requests
import time
from django.core.management.base import BaseCommand
from music.models import Song 

class Command(BaseCommand):
    help = 'SQLite verilerini Vespa.ai formatına çevirip yükler (Mock Embedding ile)'

    def handle(self, *args, **kwargs):
        vespa_host = "http://vespa-node:8080" 
        doc_api_path = "/document/v1/music/song/docid" # music: namespace, song: document type

        songs = Song.objects.all()
        self.stdout.write(f"Toplam {len(songs)} şarkı bulundu. Vespaya senkronizasyon başlıyor..")

        # Rastgele atamak için tür listesi
        genres = ["Rock", "Pop", "Jazz", "Hip-Hop", "Electronic", "Classical", "Indie"]

        success_count = 0
        fail_count = 0

        for song in songs:
            # --- 1. VERİ ZENGİNLEŞTİRME (DATA ENRICHMENT) ---
            
            # Eğer genre yoksa rastgele ata
            current_genre = song.genre if song.genre else random.choice(genres)
            
            # Eğer popularity 0 ise rastgele ata
            current_popularity = song.popularity if song.popularity > 0 else random.randint(10, 100)


            # şarkı id sini seed olarak kullanıyoruz böylece her üretimde aynı vektörü üretiriz
            random.seed(song.id) 
            
            # 3 boyutlu örnek vektör rastgele verktör üretimi
            mock_embedding = {
                "values": [random.random(), random.random(), random.random()]
            }

            # vespa ya gönderilecek veri 
            vespa_data = {
                "fields": {
                    "song_id": song.id,      
                    "title": song.title,
                    "artist": song.artist,
                    "genre": current_genre,
                    "popularity": current_popularity,
                    "embedding": mock_embedding, 
                    "stream_url": song.stream_url 
                }
            }

            # Vespa ya post etme
            url = f"{vespa_host}{doc_api_path}/{song.id}" 
            
            try:
                #şarkı verisini vespaya gönder
                response = requests.post(url, json=vespa_data)
                
                if response.status_code == 200:
                    success_count += 1
                else:
                    fail_count += 1
                    self.stdout.write(self.style.ERROR(f"HATA ({response.status_code}): {song.title} - {response.text}"))
            
            except requests.exceptions.RequestException as e:
                fail_count += 1
                self.stdout.write(self.style.ERROR(f"BAĞLANTI HATASI: {song.title} -> {str(e)}"))

        self.stdout.write(self.style.SUCCESS(f"\nİşlem Tamamlandı! Başarılı: {success_count}, Hatalı: {fail_count}"))