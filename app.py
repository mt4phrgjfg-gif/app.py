
from gtts import gTTs
import base64
import io
def sesli_cevap(metin):
    try:
        tts = gTTS(text=metin[:200], lang="tr", slow=False)
        ses_buffer = io.BytesIO()
        tts.write_to_fp(ses_buffer)
        ses_buffer.seek(0)
        ses_b64 = base64.b64encode(ses_buffer.read()).decode()
        st.markdown(f"""
            <audio autoplay>
                <source src="data:audio/mp3;base64,{ses_b64}" type="audio/mp3">
            </audio>
        """, unsafe_allow_html=True)
    except:
        pass
sesli_cevap(yanit)
 import streamlit as st
import re
import math
import requests
import json
import os
from datetime import datetime

st.set_page_config(page_title="Prime Brain", page_icon="🧠")
st.title("🧠 Prime Brain")
st.caption("📖 Wikipedia • 🌤 Hava • 💱 Döviz • 🔢 Matematik • 🧠 Öğrenen AI")

# ============================================================
# HAFIZA — Öğrenilen bilgileri kaydet
# ============================================================
HAFIZA_DOSYA = "prime_brain.json"

def hafiza_yukle():
    if os.path.exists(HAFIZA_DOSYA):
        try:
            with open(HAFIZA_DOSYA, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            pass
    return {
        "ogrenilenler": {},
        "duzeltmeler": {},
        "sohbet_sayisi": 0,
        "basarili_cevaplar": 0,
        "basarisiz_cevaplar": 0
    }

def hafiza_kaydet(hafiza):
    with open(HAFIZA_DOSYA, "w", encoding="utf-8") as f:
        json.dump(hafiza, f, ensure_ascii=False, indent=2)

# ============================================================
# MATEMATİK
# ============================================================
def matematik_coz(soru):
    s = soru.strip()
    s = s.replace("×","*").replace("÷","/").replace("^","**")
    s = s.replace("x","*").replace("X","*")
    s = s.replace("artı","+").replace("eksi","-")
    s = s.replace("çarpı","*").replace("bölü","/")
    s = s.replace(",",".").replace("=","").strip()
    temiz = s.lower()

    if "karekök" in temiz:
        n = re.findall(r"\d+\.?\d*", temiz)
        if n: return f"√{n[0]} = {math.sqrt(float(n[0])):.6g}"
    if "faktoriyel" in temiz:
        n = re.findall(r"\d+", temiz)
        if n and int(n[0])<=20: return f"{n[0]}! = {math.factorial(int(n[0]))}"
    if "sin" in temiz:
        n = re.findall(r"\d+\.?\d*", temiz)
        if n: return f"sin({n[0]}°) = {math.sin(math.radians(float(n[0]))):.6g}"
    if "cos" in temiz:
        n = re.findall(r"\d+\.?\d*", temiz)
        if n: return f"cos({n[0]}°) = {math.cos(math.radians(float(n[0]))):.6g}"
    if "tan" in temiz:
        n = re.findall(r"\d+\.?\d*", temiz)
        if n: return f"tan({n[0]}°) = {math.tan(math.radians(float(n[0]))):.6g}"
    if "pisagor" in temiz:
        n = re.findall(r"\d+\.?\d*", temiz)
        if len(n)>=2: return f"c = {math.sqrt(float(n[0])**2+float(n[1])**2):.6g}"
    if "yüzde" in temiz or "%" in temiz:
        n = re.findall(r"\d+\.?\d*", temiz)
        if len(n)>=2: return f"%{n[0]} × {n[1]} = {float(n[0])*float(n[1])/100:.6g}"
    if "ortalama" in temiz:
        n = re.findall(r"\d+\.?\d*", temiz)
        if n:
            nums = [float(x) for x in n]
            return f"Ortalama = {sum(nums)/len(nums):.6g}"
    if "log" in temiz:
        n = re.findall(r"\d+\.?\d*", temiz)
        if n: return f"log({n[0]}) = {math.log10(float(n[0])):.6g}"
    if "pi" in temiz:
        return f"π = {math.pi:.10g}"
    try:
        ifade = re.sub(r"[^0-9+\-*/().**]","",s).strip()
        if ifade and len(ifade)>=3 and re.search(r"\d",ifade):
            sonuc = eval(ifade)
            if sonuc == int(sonuc): return f"{ifade} = {int(sonuc)}"
            return f"{ifade} = {sonuc:.6g}"
    except:
        pass
    return None

# ============================================================
# WIKIPEDIA
# ============================================================
def soru_analiz(mesaj):
    m = mesaj.lower().strip()
    temizle = ["nedir","kimdir","ne demek","hakkında","anlat",
               "açıkla","söyle","bilgi ver","nerede","nasıl",
               "neden","niçin","hangi","kaç tane","kaç"]
    for k in temizle:
        m = m.replace(k," ")
    m = re.sub(r"[^\w\s]","",m)
    m = re.sub(r"\s+"," ",m).strip()
    return m if len(m)>1 else mesaj

def wikipedia_ara(sorgu):
    try:
        arama = f"https://tr.wikipedia.org/w/api.php?action=query&list=search&srsearch={requests.utils.quote(sorgu)}&format=json&srlimit=5"
        r = requests.get(arama, timeout=6, headers={"User-Agent":"PrimeBrain/1.0"})
        if r.status_code != 200: return None, None
        sonuclar = r.json().get("query",{}).get("search",[])
        for sonuc in sonuclar:
            baslik = sonuc["title"]
            url = (f"https://tr.wikipedia.org/w/api.php?action=query"
                   f"&titles={requests.utils.quote(baslik)}"
                   f"&prop=extracts&exintro=true&explaintext=true&format=json")
            r2 = requests.get(url, timeout=6)
            if r2.status_code == 200:
                pages = r2.json().get("query",{}).get("pages",{})
                for page in pages.values():
                    icerik = page.get("extract","").strip()
                    icerik = re.sub(r"\n+","\n",icerik)
                    if len(icerik)>100:
                        return baslik, icerik[:1200]
    except:
        pass
    return None, None

# ============================================================
# HAVA & DÖVİZ
# ============================================================
def hava_durumu(sehir):
    try:
        r = requests.get(f"https://wttr.in/{requests.utils.quote(sehir)}?format=3", timeout=5)
        if r.status_code == 200: return r.text.strip()
    except:
        pass
    return None

def doviz_kuru(m):
    try:
        r = requests.get("https://api.exchangerate-api.com/v4/latest/USD", timeout=5)
        if r.status_code == 200:
            rates = r.json()["rates"]
            tl = rates.get("TRY",0)
            eur = rates.get("EUR",0)
            gbp = rates.get("GBP",0)
            if "euro" in m or "eur" in m: return f"1 EUR = {tl/eur:.2f} TL"
            if "sterlin" in m or "gbp" in m: return f"1 GBP = {tl/gbp:.2f} TL"
            return f"1 USD = {tl:.2f} TL\n1 EUR = {tl/eur:.2f} TL\n1 GBP = {tl/gbp:.2f} TL"
    except:
        pass
    return None

# ============================================================
# ANA CEVAP MOTORU
# ============================================================
def cevap_uret(mesaj, hafiza):
    m = mesaj.lower().strip()

    # 1. Öğrenilmiş bilgileri kontrol et
    for anahtar, deger in hafiza["ogrenilenler"].items():
        if anahtar in m:
            return "🧠 Öğrenilmiş", deger

    # 2. Düzeltmeleri kontrol et
    for yanlis, dogru in hafiza["duzeltmeler"].items():
        if yanlis in m:
            return "✅ Düzeltilmiş", dogru

    # 3. Hava durumu
    if "hava durumu" in m or "hava nasıl" in m:
        sehirler = ["istanbul","ankara","izmir","bursa","antalya","adana",
                    "konya","gaziantep","kayseri","trabzon","samsun",
                    "eskişehir","mersin","diyarbakır","erzurum","van"]
        for sehir in sehirler:
            if sehir in m:
                sonuc = hava_durumu(sehir)
                if sonuc: return "🌤️ Hava Durumu", sonuc
        return "🌤️ Hava Durumu", hava_durumu("Istanbul")

    # 4. Döviz
    doviz_k = ["dolar kaç","euro kaç","döviz","dolar ne kadar","euro ne kadar","sterlin"]
    if any(k in m for k in doviz_k):
        sonuc = doviz_kuru(m)
        if sonuc: return "💱 Güncel Kurlar", sonuc

    # 5. Matematik
    matematik_k = ["+","-","*","/","karekök","sin","cos","tan",
                   "pisagor","yüzde","%","faktoriyel","ortalama","log","pi"]
    if any(k in m for k in matematik_k) or re.search(r"\d+[\s]*[x×÷\+\-\*\/][\s]*\d+",m):
        sonuc = matematik_coz(mesaj)
        if sonuc: return "🔢 Matematik", sonuc

    # 6. Wikipedia
    anahtar = soru_analiz(mesaj)
    if len(anahtar) > 1:
        baslik, icerik = wikipedia_ara(anahtar)
        if icerik: return f"📖 {baslik}", icerik

    return None, None

# ============================================================
# UI
# ============================================================
if "sohbet" not in st.session_state:
    st.session_state.sohbet = []
if "hafiza" not in st.session_state:
    st.session_state.hafiza = hafiza_yukle()

hafiza = st.session_state.hafiza

# İstatistikler
col1, col2, col3 = st.columns(3)
col1.metric("Sohbet", hafiza["sohbet_sayisi"])
col2.metric("Öğrenilen", len(hafiza["ogrenilenler"]))
col3.metric("Düzeltme", len(hafiza["duzeltmeler"]))

st.divider()

# Geçmiş mesajlar
for msg in st.session_state.sohbet:
    with st.chat_message(msg["rol"]):
        if msg.get("baslik"):
            st.subheader(msg["baslik"])
        st.write(msg["icerik"])

# Kullanıcı girişi
if mesaj := st.chat_input("Bir şey sor..."):
    with st.chat_message("user"):
        st.write(mesaj)
    st.session_state.sohbet.append({"rol":"user","icerik":mesaj})
    hafiza["sohbet_sayisi"] += 1

    with st.chat_message("assistant"):
        with st.spinner("Düşünüyor..."):
            baslik, yanit = cevap_uret(mesaj, hafiza)

            if yanit:
                if baslik: st.subheader(baslik)
                st.write(yanit)
                hafiza["basarili_cevaplar"] += 1

                # Geri bildirim butonları
                col1, col2 = st.columns(2)
                begendi = col1.button("👍 Doğru", key=f"b{hafiza['sohbet_sayisi']}")
                begenMedi = col2.button("👎 Yanlış", key=f"y{hafiza['sohbet_sayisi']}")

                if begendi:
                    # Doğru cevabı öğren
                    anahtar = soru_analiz(mesaj).lower()[:50]
                    hafiza["ogrenilenler"][anahtar] = yanit
                    hafiza_kaydet(hafiza)
                    st.success("✅ Öğrendim!")

                if begenMedi:
                    st.session_state.duzeltme_bekleniyor = mesaj
                    st.warning("Doğru cevabı yazar mısın?")
            else:
                yanit = "Bu konuda bilgi bulamadım. Bana öğretir misin?"
                st.warning(yanit)
                hafiza["basarisiz_cevaplar"] += 1

    st.session_state.sohbet.append({
        "rol":"assistant",
        "baslik": baslik,
        "icerik": yanit
    })
    hafiza_kaydet(hafiza)
    st.session_state.hafiza = hafiza

# Düzeltme girişi
if "duzeltme_bekleniyor" in st.session_state:
    dogru = st.text_input("✏️ Doğru cevap nedir?")
    if dogru and st.button("Kaydet"):
        yanlis_soru = soru_analiz(st.session_state.duzeltme_bekleniyor).lower()[:50]
        hafiza["duzeltmeler"][yanlis_soru] = dogru
        hafiza["ogrenilenler"][yanlis_soru] = dogru
        hafiza_kaydet(hafiza)
        del st.session_state.duzeltme_bekleniyor
        st.success("✅ Düzeltme kaydedildi! Bir dahaki sefere doğru cevabı vereceğim.")
        st.rerun()
