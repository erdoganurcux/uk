from flask import Flask, render_template
from veriler import harem_veri_cek, AltinFiyatScraper, FiyatHesaplayici

app = Flask(__name__)

@app.route('/')
def index():
    # Harem'den veri çek
    veri_harem = harem_veri_cek()

    if veri_harem:
        has_altin_alis_fiyati = float(veri_harem.get('ALTIN', {}).get('alis', 0.0))
        has_altin_satis_fiyati = float(veri_harem.get('ALTIN', {}).get('satis', 0.0))

        # Akod'dan veri çek
        url_akod = 'http://www.akod.org.tr'
        scraper_akod = AltinFiyatScraper(url_akod)
        altin_adlari_akod, satis_fiyatlari_akod, alis_fiyatlari_akod, tarih_saat_akod = scraper_akod.scrape_altin_fiyatlari(has_altin_alis_fiyati, has_altin_satis_fiyati)

        if altin_adlari_akod and satis_fiyatlari_akod:
            akod_data = []

            for altin_adi_akod, satis_fiyati_akod, alis_fiyati_akod in zip(altin_adlari_akod, satis_fiyatlari_akod, alis_fiyatlari_akod):
                hesaplayici_akod = FiyatHesaplayici(alis_fiyati_akod, satis_fiyati_akod)
                fiyat_farki_yuzdesi_akod = hesaplayici_akod.fiyat_farki_yuzdesi()
                akod_data.append({
                    'altin_adi': altin_adi_akod,
                    'alis_fiyati': alis_fiyati_akod,
                    'satis_fiyati': satis_fiyati_akod,
                    'fiyat_farki_yuzdesi': fiyat_farki_yuzdesi_akod,
                    'tarih_saat': tarih_saat_akod
                })

            # Harem'den ek veri çek
            dolar_try_data = veri_harem.get('USDTRY', {})
            euro_try_data = veri_harem.get('EURTRY', {})
            gumus_try_data = veri_harem.get('GUMUSTRY', {})
            has_altin_data = veri_harem.get('ALTIN', {})
            ons_altin_data = veri_harem.get('ONS', {})

            if dolar_try_data and euro_try_data and gumus_try_data and has_altin_data and ons_altin_data:
                istenen_veriler = {
                    'Dolar/TL': {'Alış': float(dolar_try_data.get('alis', 0.0)), 'Satış': float(dolar_try_data.get('satis', 0.0))},
                    'Euro/TL': {'Alış': float(euro_try_data.get('alis', 0.0)), 'Satış': float(euro_try_data.get('satis', 0.0))},
                    'Gümüş/TL': {'Alış': float(gumus_try_data.get('alis', 0.0)), 'Satış': float(gumus_try_data.get('satis', 0.0))},
                    'Has Altın': {'Alış': float(has_altin_data.get('alis', 0.0)), 'Satış': float(has_altin_data.get('satis', 0.0))},
                    'Ons Altın': {'Alış': float(ons_altin_data.get('alis', 0.0)), 'Satış': float(ons_altin_data.get('satis', 0.0))},
                    '24 Ayar Gram Altın': {'Alış': has_altin_alis_fiyati * 0.990, 'Satış': has_altin_satis_fiyati * 1.020},
                }

                doviz_data = []

                for key, value in istenen_veriler.items():
                    hesaplayici_doviz = FiyatHesaplayici(value['Alış'], value['Satış'])
                    fiyat_farki_yuzdesi_doviz = hesaplayici_doviz.fiyat_farki_yuzdesi()
                    doviz_data.append({
                        'doviz_adi': key,
                        'alis_fiyati': value['Alış'],
                        'satis_fiyati': value['Satış'],
                        'fiyat_farki_yuzdesi': fiyat_farki_yuzdesi_doviz,
                        'tarih_saat': tarih_saat_akod
                    })

                return render_template('index.html', akod_data=akod_data, doviz_data=doviz_data)
            else:
                return render_template('index.html', akod_data=akod_data, doviz_data=None)

    return render_template('index.html', akod_data=None, doviz_data=None)

if __name__ == '__main__':
    app.run(debug=True)