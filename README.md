# 🎵 Spotify Öneri Motoru Prototipi (Vespa.ai & Django)

Sistem, Approximate Nearest Neighbor (ANN) algoritması (HNSW graph yapısı) ve özel sıralama (ranking) profilleri kullanarak kullanıcı profiline uygun şarkı önerileri sunar.

## 🚀 Hızlı Kurulum ve Çalıştırma Rehberi

Projeyi yerel ortamınızda test etmek için bilgisayarınızda **Docker** ve **Docker Compose** kurulu olmalıdır.

### 🔹 Adım 1: Altyapıyı Ayağa Kaldırın

Proje dizininde terminali açın ve tüm mikroservisleri (Vespa, Django, SeaweedFS) arka planda başlatın:

```bash
docker-compose up -d
```

*(Not: Vespa'nın tamamen ayağa kalkıp istek kabul etmeye başlaması sistemin hızına göre 30 saniye – 1 dakika sürebilir. Lütfen 2. adıma geçmeden önce kısa bir süre bekleyin.)*

### 🔹 Adım 2: Vespa Şemasını Yükleyin (Deploy)

Vespa'nın `song.sd` şemasını ve ayarlarını sisteme tanımlamak için aşağıdaki komutu çalıştırın.

**Linux / Git Bash kullanıcıları için:**
```bash
curl --header "Content-Type:application/zip" --data-binary @vespa-app.zip http://localhost:19071/application/v2/tenant/default/prepareandactivate
```

**Windows PowerShell kullanıcıları için:**
```powershell
curl.exe --header "Content-Type:application/zip" --data-binary @vespa-app.zip http://localhost:19071/application/v2/tenant/default/prepareandactivate
```

Ekranda aşağıdaki mesajı görüyorsanız Vespa başarıyla yapılandırılmıştır:
`"message": "Session X for tenant 'default' prepared and activated."`

### 🔹 Adım 3: Verileri Vespa'ya Senkronize Edin

Proje içerisinde hazır bir `db.sqlite3` veritabanı bulunmaktadır. Bu veritabanındaki örnek şarkıların vektörleştirilip (mock embedding) Vespa nın belleğine  yüklenmesi için Django konteynerinin içine aşağıdaki komutu gönderin:

```bash
docker exec -it django_backend python manage.py sync_vespa
```

### 🔹 Adım 4: Sistemi Test Edin (API İstekleri)

Sistem başarıyla kuruldu 🎉

Artık tarayıcınızdan veya Postman üzerinden API'yi çağırarak farklı sıralama stratejilerini test edebilirsiniz:

* 🎯 **Sadece Benzerlik Odaklı Sıralama (Similarity Ranking)**
  [http://localhost:8000/api/music/recommendations/?strategy=similarity_ranking](http://localhost:8000/api/music/recommendations/?strategy=similarity_ranking)

* 🎯 **Benzerlik + Popülerlik Odaklı Hibrit Sıralama (Hybrid Ranking)**
  [http://localhost:8000/api/music/recommendations/?strategy=hybrid_ranking](http://localhost:8000/api/music/recommendations/?strategy=hybrid_ranking)

---

## 🛠️ Tasarım Kararları ve Bilinmesi Gerekenler


### 🎵 Müzik Dosyaları ve SeaweedFS
Mimaride medya dosyalarının veritabanını şişirmemesi adına SeaweedFS kullanılmıştır. Ancak repository boyutunu optimize etmek için fiziksel MP3 dosyaları (`seaweedfs_data` klasörü) repoya eklenmemiştir.

API’den dönen JSON yanıtlarındaki `url` alanları mimarinin doğru çalıştığını gösterir. Ancak bu linklere tıklandığında fiziksel dosyalar projede olmadığı için *404 Not Found* dönmesi beklenen bir prototip davranışıdır.

### 🧠 Mock Embedding
Şarkıların müzikal özellikleri 3 boyutlu vektörler olarak simüle edilmiştir. Test sonuçlarının deterministik ve tutarlı olması adına vektörler:

```python
random.seed(song_id)
```
kullanılarak sabitlenmiştir.