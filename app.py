```python
import streamlit as st
import requests
from bs4 import BeautifulSoup
import json
import os
import re
import urllib.parse

# --- ARAYÜZ AYARLARI ---
st.set_page_config(page_title="AI Araştırma İstemcisi", layout="wide")
DB_FILE = "veritabani.json"

# --- VERİTABANI YÖNETİMİ ---
def veritabani_yukle():
    if not os.path.exists(DB_FILE):
        with open(DB_FILE, "w", encoding="utf-8") as f:
            json.dump({}, f)
    try:
        with open(DB_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}

def veritabani_kaydet(anahtar, deger):
    veri = veritabani_yukle()
    veri[anahtar.lower()] = deger
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(veri, f, ensure_ascii=False, indent=4)

# --- MATEMATİK MOTORU ---
def matematik_coz(ifade):
    # 'x' harfini çarpma işlemine çevir, boşlukları sil
    ifade_temiz = ifade.lower().replace(" ", "").replace("x", "*")
    
    # Sadece sayı ve temel operatörler içeriyorsa hesapla
    if re.match(r'^[\d\+\-\*\/\(\)\.]+$', ifade_temiz):
        try:
            return eval(ifade_temiz)
        except Exception:
            return None
    return None

# --- GERÇEK İNTERNET VE VPN (PROXY) MOTORU ---
def gercek_internet_aramasi(sorgu, proxy_url):
    proxies = {}
    # Kullanıcı proxy girdiyse, trafiği o ağa yönlendir
    if proxy_url:
        proxies = {
            "http": proxy_url,
            "https": proxy_url
        }
    
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
    url = f"https://html.duckduckgo.com/html/?q={urllib.parse.quote(sorgu)}"
    
    try:
        cevap = requests.get(url, headers=headers, proxies=proxies, timeout=10)
        soup = BeautifulSoup(cevap.text, 'html.parser')
        sonuclar = soup.find_all('a', class_='result__snippet')
        
        if not sonuclar:
            return "İnternette sonuç bulunamadı."
            
        ozet = ""
        for sonuc in sonuclar[:4]:  # İlk 4 sonucu getir
            ozet += f"- {sonuc.text}\n"
        return ozet
    except Exception as e:
        return f"İnternet bağlantı hatası: {str(e)}\n(Eğer proxy kullandıysanız, girdiğiniz proxy adresi çalışmıyor olabilir.)"

# --- ANA UYGULAMA DÖNGÜSÜ ---
def main():
    st.title("Araştırma ve Hesaplama Asistanı")
    st.markdown("İşlev odaklı, stabil altyapı. İnternet araması, matematik motoru ve proxy desteği içerir.")

    # --- YAN MENÜ: AĞ VE VERİTABANI AYARLARI ---
    with st.sidebar:
        st.header("Ağ Ayarları (VPN/Proxy)")
        st.markdown("Trafiğinizi şifrelemek ve IP gizlemek için çalışan bir proxy girin.")
        
        # Kullanıcı buraya "http://12.34.56.78:8080" gibi bir proxy girdiğinde internet aramaları oradan yapılır.
        proxy_input = st.text_input("Proxy Adresi:", placeholder="http://ip:port veya socks5://ip:port")
        
        if proxy_input:
            st.success("Ağ yönlendirmesi aktif. İstekler proxy üzerinden çıkacak.")
        
        st.divider()
        st.header("Yerel Veritabanı")
        db = veritabani_yukle()
        st.write(f"Kayıtlı Veri Sayısı: {len(db)}")

    # --- SOHBET / İŞLEM GEÇMİŞİ ---
    if "mesajlar" not in st.session_state:
        st.session_state.mesajlar = []

    for mesaj in st.session_state.mesajlar:
        with st.chat_message(mesaj["rol"]):
            st.markdown(mesaj["icerik"])

    # --- KULLANICI GİRİŞİ ---
    kullanici_girdisi = st.chat_input("8x8 yazın, soru sorun veya Öğren: X = Y yazın...")

    if kullanici_girdisi:
        # Kullanıcının mesajını ekrana bas
        st.session_state.mesajlar.append({"rol": "user", "icerik": kullanici_girdisi})
        with st.chat_message("user"):
            st.markdown(kullanici_girdisi)

        with st.chat_message("assistant"):
            yanit = ""
            
            # 1. Aşama: Matematiksel işlem mi?
            mat_sonucu = matematik_coz(kullanici_girdisi)
            
            # 2. Aşama: Veritabanına kayıt komutu mu?
            if kullanici_girdisi.lower().startswith("öğren:"):
                try:
                    komut = kullanici_girdisi[6:] # "öğren:" kısmını at
                    anahtar, deger = komut.split("=", 1)
                    veritabani_kaydet(anahtar.strip(), deger.strip())
                    yanit = f"✅ Veri kaydedildi: **{anahtar.strip()}**"
                except ValueError:
                    yanit = "❌ Hatalı format. Lütfen 'Öğren: Konu = Açıklama' şeklinde yazın."
            
            # Matematik sonucu varsa yazdır
            elif mat_sonucu is not None:
                yanit = f"🧮 Hesaplama Sonucu: **{mat_sonucu}**"
            
            # 3. Aşama: Hiçbiri değilse veritabanı + internet taraması yap
            else:
                db = veritabani_yukle()
                db_yanit = ""
                
                # Önce kendi veritabanımıza bakıyoruz
                for k, v in db.items():
                    if k in kullanici_girdisi.lower():
                        db_yanit = f"🗄️ **Kayıtlı Bilgi:** {v}\n\n"
                        break
                
                # Ardından gerçek internette arıyoruz
                with st.spinner("İnternet üzerinden veri çekiliyor..."):
                    internet_yanit = gercek_internet_aramasi(kullanici_girdisi, proxy_input)
                
                yanit = db_yanit + "🌐 **İnternet Arama Sonucu:**\n" + internet_yanit

            st.markdown(yanit)
            st.session_state.mesajlar.append({"rol": "assistant", "icerik": yanit})

if __name__ == "__main__":
    main()


```
