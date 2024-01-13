import requests
from bs4 import BeautifulSoup
from datetime import datetime
from urllib import request, parse
import gzip
import json

class AltinFiyatScraper:
    def __init__(self, url):
        self.url = url
        self.altin_bilgileri = []

    def _get_html_content(self):
        try:
            response = requests.get(self.url)
            response.raise_for_status()  # Hata durumlarını kontrol et
            return response.text
        except requests.RequestException as e:
            print(f"Hata: {e}")
            return None

    def _parse_html(self, html_content):
        if html_content:
            soup = BeautifulSoup(html_content, 'html.parser')
            li_elements = soup.find_all('li')

            for li in li_elements:
                a_element = li.find('a')
                if a_element:
                    span_element = a_element.find('span')
                    fiyat_element = a_element.find('i')

                    if span_element and fiyat_element:
                        altin_turu = span_element.get_text(strip=True)
                        fiyat = fiyat_element.get_text(strip=True).replace(',', '.')

                        if altin_turu and fiyat:
                            altin_turu_display = self._map_gold_type_display(altin_turu)

                            # Tarih ve saat bilgisini gün.ay.yıl olarak formatla
                            tarih_saat = datetime.now().strftime("%d.%m.%Y %H:%M:%S")

                            altin_bilgi = {
                                'Altin Turu': altin_turu_display,
                                'Alış Fiyatı': '',  # Alış fiyatını boş bıraktım, veri yoksa
                                'Satış Fiyatı': fiyat,
                                'Tarih ve Saat': tarih_saat
                            }
                            self.altin_bilgileri.append(altin_bilgi)

    def _map_gold_type_display(self, altin_turu):
        mapping = {
            '22 Ayar Altın': '22 Ayar Gram Altın',
            'Çeyrek Ziynet': 'Çeyrek Altın',
            'Yarım Ziynet': 'Yarım Altın',
            'Tam Ziynet': 'Tam Altın'
        }
        return mapping.get(altin_turu, altin_turu)

    def scrape_altin_fiyatlari(self):
        html_content = self._get_html_content()
        self._parse_html(html_content)
        return self.altin_bilgileri


def http_istegi_gonder(url, headers, data):
    encoded_data = parse.urlencode(data).encode()

    try:
        req = request.Request(url, headers=headers, data=encoded_data)
        response = request.urlopen(req)
        return response
    except Exception as e:
        print(f"Hata oluştu: {str(e)}")
        return None

def json_verisini_cek(response):
    try:
        if response.headers.get('Content-Encoding') == 'gzip':
            compressed_data = response.read()
            data = gzip.decompress(compressed_data)
        else:
            data = response.read()

        encoding = response.headers.get_content_charset() or 'utf-8'
        result = json.loads(data.decode(encoding))
        return result.get("data")
    except json.JSONDecodeError as e:
        print(f"JSON çözme hatası: {str(e)}")
        return None

def veri_cek():
    url = 'https://www.haremaltin.com/dashboard/ajax/doviz'
    headers = {
        'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/112.0',
        'Accept': '*/*',
        'Accept-Language': 'en-US,en;q=0.5',
        'Accept-Encoding': 'gzip, deflate, br',
        'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'X-Requested-With': 'XMLHttpRequest',
        'Origin': 'https://www.haremaltin.com',
        'Connection': 'keep-alive',
        'Referer': 'https://www.haremaltin.com/canli-piyasalar/',
        'Cookie': 'PHPSESSID=1q4084qbl7qd02biui6sgak6rl; SERVERID=003',
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'same-origin',
        'DNT': '1',
        'Sec-GPC': '1'
    }
    data = {'dil_kodu': 'tr'}

    response = http_istegi_gonder(url, headers, data)

    if not response or response.status != 200:
        print(f"Veri alınamadı. Hata kodu: {response.status}")
        return None

    veri = json_verisini_cek(response)

    if not veri:
        print("Veri alınamadı.")
        return None

    return veri

def alis_satis_tarih_degisim_orani_goster(veri):
    if not veri:
        print("Veri alınamadı.")
        return

    # Altın türleri için özel isimlendirmeler
    altin_turleri_isimlendirme = {
        'USDTRY': 'Dolar/TL',
        'ALTIN': 'Has Altın',
        'EURTRY': 'Euro/TL',
        'ONS': 'Ons Altın TL'
    }

    print("Başarılı! Alınan Veri:")
    for kur, deger in veri.items():
        if kur in altin_turleri_isimlendirme:
            print(f"{altin_turleri_isimlendirme[kur]}:")
            print(f"  Alış: {deger.get('alis')}")
            print(f"  Satış: {deger.get('satis')}")
            print(f"  Tarih: {deger.get('tarih')}")

            # Alış ve satış fiyatları arasındaki değişim oranını hesapla
            alis_fiyati = float(deger.get('alis'))
            satis_fiyati = float(deger.get('satis'))
            degisim_orani = ((satis_fiyati - alis_fiyati) / alis_fiyati) * 100

            print(f"  Değişim Oranı: {round(degisim_orani, 2)}%")
            print()

    # "24 Ayar Gram Altın" için özel hesaplamalar
    altin_alis = float(veri.get('ALTIN').get('alis'))
    altin_satis = float(veri.get('ALTIN').get('satis'))
    altin_tarih = veri.get('ALTIN').get('tarih')

    altin_24_ayar_alis = round(altin_alis * 0.995, 2)  # ALTIN'ın alış fiyatını belirtilen oranla çarp
    altin_24_ayar_satis = round(altin_satis * 1.020, 2)  # ALTIN'ın satış fiyatını belirtilen oranla çarp

    print("24 Ayar Gram Altın:")
    print(f"  Alış: {altin_24_ayar_alis}")
    print(f"  Satış: {altin_24_ayar_satis}")

    # Tarih ve saat bilgisini gün.ay.yıl olarak formatla
    altin_tarih = datetime.strptime(altin_tarih, "%d-%m-%Y %H:%M:%S").strftime("%d.%m.%Y %H:%M:%S")
    print(f"  Tarih: {altin_tarih}")

    # "Alış Fiyatı ile Satış Fiyatı arasındaki değişim oranını" hesapla ve göster
    altin_degisim_orani = ((altin_24_ayar_satis - altin_24_ayar_alis) / altin_24_ayar_alis) * 100
    print(f"  24 Ayar Gram Altın Değişim Oranı: {round(altin_degisim_orani, 2)}%")

def altin_turleri_fiyatlarini_goster(altin_bilgileri, alis_fiyati_has_altin):
    if altin_bilgileri:
        for altin_turu in ['22 Ayar Gram Altın', 'Çeyrek Altın', 'Yarım Altın', 'Tam Altın', 'Cumhuriyet']:
            # Özel hesaplamalar
            if altin_turu == '22 Ayar Gram Altın':
                alis_fiyati = alis_fiyati_has_altin * 0.910
            elif altin_turu == 'Çeyrek Altın':
                alis_fiyati = alis_fiyati_has_altin * 1.60
            elif altin_turu == 'Yarım Altın':
                alis_fiyati = alis_fiyati_has_altin * 3.20
            elif altin_turu == 'Tam Altın':
                alis_fiyati = alis_fiyati_has_altin * 6.40
            elif altin_turu == 'Cumhuriyet':
                alis_fiyati = alis_fiyati_has_altin * 6.80
            else:
                alis_fiyati = 'Bilinmiyor'

            print(f"Altın Türü: {altin_turu}")
            print(f"Alış Fiyatı: {alis_fiyati}")
            
            # İlgili altın türünün bilgilerini bul
            altin_bilgi = next((bilgi for bilgi in altin_bilgileri if bilgi['Altin Turu'] == altin_turu), None)
            if altin_bilgi:
                satis_fiyati = altin_bilgi['Satış Fiyatı']
                print(f"Satış Fiyatı: {satis_fiyati}")
                
                # Alış ve satış fiyatları arasındaki değişim oranını hesapla
                alis_fiyati = float(alis_fiyati)
                satis_fiyati = float(satis_fiyati)
                degisim_orani = ((satis_fiyati - alis_fiyati) / alis_fiyati) * 100
                print(f"Değişim Oranı: {round(degisim_orani, 2)}%")
            else:
                print("Veri bulunamadı.")

            print("-" * 30)
    else:
        print("Altın fiyatları çekilemedi.")

if __name__ == "__main__":
    # Altın fiyatları çek
    altin_url = 'http://www.akod.org.tr'
    altin_scraper = AltinFiyatScraper(altin_url)
    altin_bilgileri = altin_scraper.scrape_altin_fiyatlari()

    # Alış, satış, tarih ve değişim oranı bilgilerini göster
    alis_satis_tarih_degisim_orani_goster(veri_cek())

    # Hesaplanan altın türleri fiyatlarını göster
    veri = veri_cek()

    if veri and 'ALTIN' in veri:
        has_altin_verisi = veri['ALTIN']
        alis_fiyati_has_altin = float(has_altin_verisi.get('alis'))

        # Altın fiyatlarını göster
        altin_turleri_fiyatlarini_goster(altin_bilgileri, alis_fiyati_has_altin)
    else:
        print("Veri alınamadı.")
