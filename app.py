import streamlit as st
import requests
from bs4 import BeautifulSoup
import json
import os
import time

# --- SİSTEM AYARLARI ---
# API KEY KULLANILMAZ. SİSTEM DOĞRUDAN HTML KAZIMA (SCRAPING) ÜZERİNDEN ÇALIŞIR.
st.set_page_config(page_title="Prime Omni Core v31.13", layout="wide")
HAFIZA_PATH = "prime_brain.json"

# Görsel Arayüz (Akademik Terminal Teması)
st.markdown("""
    <style>
    .stApp { background-color: #0d1117; color: #c9d1d9; font-family: 'Courier New', Courier, monospace; }
    .stTextInput>div>div>input { background-color: #010409; color: #58a6ff; border: 1px solid #30363d; border-radius: 5px; }
    .stChatMessage { border-left: 3px solid #238636; background-color: #161b22; border-radius: 0 10px 10px 0; }
    code { color: #ff7b72 !important; }
    .stButton>button { background-color: #238636; color: white; border: none; }
    </style>
    """, unsafe_allow_html=True)

# --- KATMAN 1: v26 NÖRAL HAFIZA PROTOKOLÜ ---
def hafiza_yonetimi(komut=None):
    if not os.path.exists(HAFIZA_PATH):
        with open(HAFIZA_PATH, "w", encoding="utf-8") as f:
            json.dump({"sistem": "Aktif", "versiyon": "31.13"}, f)
    
    with open(HAFIZA_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    if komut and ":" in komut:
        anahtar, deger = komut.split(":", 1)
        data[anahtar.strip().lower()] = deger.strip()
        with open(HAFIZA_PATH, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        return True, f"💾 Nöral Kayıt Başarılı: '{anahtar.strip()}'"
    return False, data

# --- KATMAN 2: v31.12 CANLI İNTERNET MOTORU (API KEYSIZ) ---
def akademik_veri_kaziyici(sorgu):
    """
    Google sonuçlarını terminal üzerinden (curl mantığıyla) kazır.
    API anahtarı istemez, gerçek zamanlı bilgi çeker.
    """
    headers = {
        "User-Agent": "Mozilla/5.0 (iPad; CPU OS 15_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.0 Mobile/15E148 Safari/604.1"
    }
    # Akademik derinlik için sorguyu modifiye et
    clean_query = sorgu.replace(" ", "+")
    url = f"https://www.google.com/search?q={clean_query}+akademik+makale+pdf+research"
    
    try:
        res = requests.get(url, headers=headers, timeout=15)
        if res.status_code != 200:
            return "⚠️ Bağlantı reddedildi. Google bot koruması aktif olabilir.", []
        
        soup = BeautifulSoup(res.text, 'html.parser')
        results = []
        
        # Google arama sonuçlarını ayıkla
        for g in soup.find_all('div', class_='tF2Cxc'):
            title = g.find('h3').text if g.find('h3') else "Belge Başlığı Yok"
            link = g.find('a')['href'] if g.find('a') else "#"
            snippet = g.find('div', class_='VwiC3b').text if g.find('div', class_='VwiC3b') else "Özet bulunamadı."
            results.append({"t": title, "l": link, "s": snippet})

        if not results:
            return "🔍 Aramada sonuç bulunamadı. Lütfen daha teknik terimler deneyin.", []
        
        return results, [r['l'] for r in results]
    except Exception as e:
        return f"⚠️ Kritik Erişim Hatası: {str(e)}", []

# --- KATMAN 3: v30 OTONOM ROBOTİK ANALİZ ---
def robotik_kod_ureteci(p_l):
    if any(x in p_l for x in ["robot", "kod", "motor", "pid", "arduino", "python"]):
        return """
```python
# Başmühendis için Otonom Kontrol Bloğu (v30)
class PrimeRobot:
    def __init__(self):
        self.gain = 1.85
        self.status = "Aktif"
        
    def calibrate(self):
        print(f"Sistem {self.gain} çarpanı ile optimize ediliyor...")
        return "Kalibrasyon Tamamlandı"

robot = PrimeRobot()
robot.calibrate()

"""
return None
--- ANA DÖNGÜ VE KONTROL PANELİ ---
def main():
st.title("🦉 Asistan Prime: Omni Core v31.13")
st.info("Hafıza: v26 | Robotik: v30 | Akademik: v31 | Erişim: API-Key-Free (Live)")
_, hafiza = hafiza_yonetimi()
if "messages" not in st.session_state:
st.session_state.messages = []
# Mesaj Geçmişi
for message in st.session_state.messages:
with st.chat_message(message["role"]):
st.markdown(message["content"])
# Girdi Alanı
if prompt := st.chat_input("Komut girin (Örn: 'Karadelik : Çok yoğun cisim' veya 'Karadeliklerin olay ufku nedir?')"):
st.session_state.messages.append({"role": "user", "content": prompt})
with st.chat_message("user"):
st.markdown(prompt)
p_l = prompt.lower()
with st.chat_message("assistant"):
# 1. HAFIZA KAYDI MI?
is_mem, mem_res = hafiza_yonetimi(prompt)
if is_mem:
st.success(mem_res)
st.session_state.messages.append({"role": "assistant", "content": mem_res})
else:
# 2. ROBOTİK KOD VAR MI?
robot_code = robotik_kod_ureteci(p_l)
# 3. İNTERNETTEN VERİ ÇEKME
with st.spinner("🌐 İnternet katmanları taranıyor (API Key'siz Erişim)..."):
# Yerel Hafıza Check
found_mem = next((v for k, v in hafiza.items() if k in p_l), None)
if found_mem:
st.info(f"💡 Yerel Hafıza Kaydı: {found_mem}")
# Canlı Arama
arama_sonuclari, linkler = akademik_veri_kaziyici(prompt)
if isinstance(arama_sonuclari, list):
response = "### 📚 Canlı Akademik Sentez\n\n"
for res in arama_sonuclari[:3]:
response += f"{res['t']}\n{res['s']}\n\n"
if robot_code:
response += f"\n---\n{robot_code}"
st.markdown(response)
if linkler:
st.divider()
st.markdown("🔗 Kaynakça:")
for l in linkler[:3]: st.markdown(f"- {l}")
st.session_state.messages.append({"role": "assistant", "content": response})
else:
st.error(arama_sonuclari)
st.session_state.messages.append({"role": "assistant", "content": arama_sonuclari})
if name == "main":
main()

