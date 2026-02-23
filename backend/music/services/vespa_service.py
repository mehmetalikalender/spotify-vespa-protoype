import requests

class VespaService:
    def __init__(self):
        # Docker ağı içindeki adres
        self.base_url = "http://vespa-node:8080/search/"

    def recommend(self, user_vector, strategy="similarity_ranking"):
        # YQL sorgusu dışardan gelen vektör ile song şemasından en yakın vektöre sahip 10 şarkıyı bul
        yql = 'select * from song where {targetHits: 10}nearestNeighbor(embedding, user_vector)'
        
        # Vespanın anlayacağı paket
        payload = {
            'yql': yql,
            'ranking': strategy,
            'input.query(user_vector)': { "values": user_vector },
            'hits': 5 #Target hits ile en iyi 10 tane bulundu ama kullanıcıya en iyi 5 taneyi göster
        }
        
        try:
            response = requests.post(self.base_url, json=payload)
            if response.status_code == 200:
                return response.json()
            else:
                # Hata kodunu terminalde görmek için:
                print(f"VESPA HATASI: {response.status_code} - {response.text}")
                return None
        except Exception as e:
            print(f"BAĞLANTI HATASI: {str(e)}")
            return None