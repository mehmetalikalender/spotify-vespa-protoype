import requests
from django.conf import settings

class SeaweedFSService:
    MASTER_URL = settings.SEAWEEDFS_MASTER_URL

    @staticmethod
    def upload_file(file_obj):
        """
        Dosyayı alır  master servisinden yer ister ve ilgili Volume sunucusuna yükler
        """
        #  masterdan yer iste /dir/assign
        try:
            assign_response = requests.get(f"{SeaweedFSService.MASTER_URL}/dir/assign")
            assign_response.raise_for_status()
            data = assign_response.json()
        except requests.RequestException as e:
            raise Exception(f"SeaweedFS Master'a erişilemiyor: {str(e)}")

        fid = data.get('fid')
        # Master bize hem iç IP  hem dış IP (publicUrl) verebilir.
        volume_url = data.get('url') 
        
        if not fid or not volume_url:
            raise Exception("SeaweedFS geçerli bir fid veya url döndürmedi.")

        # Yukleme islemini Docker ic ağından  yapıyoruz
        upload_endpoint = f"http://{volume_url}/{fid}"
        
        # Dosya gönderilir uygun formata dönüştür
        file_obj.seek(0)
        files = {'file': (file_obj.name, file_obj, file_obj.content_type)}
        try:
            upload_response = requests.post(upload_endpoint, files=files)
            upload_response.raise_for_status() #Hata durumunda exception fırlat yoksa devam et
        except requests.RequestException as e:
            raise Exception(f"Volume sunucusuna dosya yüklenemedi: {str(e)}")

    
        stream_url = f"http://{volume_url}/{fid}"

        return fid, stream_url # strean url ve FID döndür

    @staticmethod
    def get_file_url(file_id):
        """
        Dosyanın güncel Localhost adresini master dan sorgular.
        """
        if not file_id:
            return None

        volume_id = file_id.split(',')[0]  
        
        try:
            # Master'a sor: "Bu volume nerede?"
            lookup_url = f"{SeaweedFSService.MASTER_URL}/dir/lookup?volumeId={volume_id}"
            response = requests.get(lookup_url)
            
            if response.status_code == 200:
                data = response.json()
                if 'locations' in data and len(data['locations']) > 0:
                    # Docker-compose'daki -publicUrl değerini al
                    public_base_url = data['locations'][0]['publicUrl']
                    return f"http://{public_base_url}/{file_id}"
                    
        except Exception as e:
            print(f"SeaweedFS Lookup Hatası: {e}")
            
        return None
    
"""
{
  "volumeId": "3",
  "locations": [
    {
      "url": "172.19.0.5:8080",       // Docker İç IP'si
      "publicUrl": "localhost:8080"   // yml dosyasına volume server a yazılan url bilgisi
    }
  ]
}"""