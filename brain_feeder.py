import json
import requests
from xml.etree import ElementTree

HAFIZA_DOSYASI = "prime_brain.json"

def nasa_haberlerini_cek():
    print("🚀 NASA verileri taranıyor...")
    rss_url = "https://www.nasa.gov/rss/dyn/breaking_news.rss"
    response = requests.get(rss_url)
    tree = ElementTree.fromstring(response.content)
    
    yeni_bilgiler = {}
    for item in tree.findall('./channel/item')[:3]: # En güncel 3 haberi al
        baslik = item.find('title').text.lower()
        ozet = item.find('description').text
        yeni_bilgiler[baslik] = ozet
    return yeni_bilgiler

def hafizayi_guncelle(yeni_veriler):
    with open(HAFIZA_DOSYASI, "r", encoding="utf-8") as f:
        mevcut_hafiza = json.load(f)
    
    mevcut_hafiza.update(yeni_veriler)
    
    with open(HAFIZA_DOSYASI, "w", encoding="utf-8") as f:
        json.dump(mevcut_hafiza, f, ensure_ascii=False, indent=4)
    print("✅ Hafıza güncellendi!")

if __name__ == "__main__":
    yeni_haberler = nasa_haberlerini_cek()
    hafizayi_guncelle(yeni_haberler)
