import streamlit as st
import re
import math
import requests

st.set_page_config(page_title="Prime Brain", page_icon="🧠")
st.title("🧠 Prime Brain")
st.caption("📖 Wikipedia • 🌤️ Hava • 💱 Döviz • 🔢 Matematik")

# ============================================================
# SORU ANALİZİ — Sorudan anahtar kelimeyi çıkar
# ============================================================
def soru_analiz(mesaj):
    m = mesaj.lower().strip()
    
    # Gereksiz kelimeleri temizle
    temizle = [
        "nedir","kimdir","ne demek","hakkında","anlat","açıkla",
        "söyle","bilgi ver","öğrenmek istiyorum","bana anlat",
        "kim","ne","nerede","nasıl","neden","niçin","hangi",
        "şu","bu","bir","var mı","var","yok","mı","mi","mu","mü",
        "lütfen","acaba","peki","yani","şey"
    ]
    
    temiz = m
    for k in temizle:
        temiz = temiz.replace(k, " ")
    
    # Noktalama temizle
    temiz = re.sub(r"[^\w\s]", "", temiz)
    temiz = re.sub(r"\s+", " ", temiz).strip()
    
    return temiz if len(temiz) > 1 else mesaj

def wikipedia_ara(sorgu):
    try:
        # Türkçe Wikipedia'da arama yap
        arama_url = f"https://tr.wikipedia.org/w/api.php?action=query&list=search&srsearch={requests.utils.quote(sorgu)}&format=json&srlimit=5"
        r = requests.get(arama_url, timeout=6, headers={"User-Agent": "PrimeBrain/1.0"})
        if r.status_code != 200:
            return None, None
            
        sonuclar = r.json().get("query", {}).get("search", [])
        if not sonuclar:
            return None, None

        # En alakalı sonucu al
        for sonuc in sonuclar:
            baslik = sonuc["title"]
            
            # İçeriği getir
            icerik_url = (
                f"https://tr.wikipedia.org/w/api.php?"
                f"action=query&titles={requests.utils.quote(baslik)}"
                f"&prop=extracts&exintro=true&explaintext=true&format=json"
            )
            r2 = requests.get(icerik_url, timeout=6)
            if r2.status_code != 200:
                continue
                
            pages = r2.json().get("query", {}).get("pages", {})
            for page in pages.values():
                icerik = page.get("extract", "").strip()
                icerik = re.sub(r"\n+", "\n", icerik)
                
                # En az 100 karakter olsun
                if len(icerik) > 100:
                    return baslik, icerik[:1200]
                    
    except Exception as e:
        return None, None
    return None, None

def hava_durumu(sehir):
    try:
        url = f"https://wttr.in/{requests.utils.quote(sehir)}?format=3"
        r = requests.get(url, timeout=5)
        if r.status_code == 200:
            return r.text.strip()
    except:
        pass
    return None

def doviz_kuru(m):
    try:
        url = "https://api.exchangerate-api.com/v4/latest/USD"
        r = requests.get(url, timeout=5)
        if r.status_code == 200:
            rates = r.json()["rates"]
            tl  = rates.get("TRY", 0)
            eur = rates.get("EUR", 0)
            gbp = rates.get("GBP", 0)
            if "euro" in m or "eur" in m:
                return f"1 EUR = {tl/eur:.2f} TL"
            if "sterlin" in m or "gbp" in m:
                return f"1 GBP = {tl/gbp:.2f} TL"
            return f"1 USD = {tl:.2f} TL\n1 EUR = {tl/eur:.2f} TL\n1 GBP = {tl/gbp:.2f} TL"
    except:
        pass
    return None

def matematik_coz(soru):
    s = soru.lower()
    s = s.replace("artı","+").replace("eksi","-")
    s = s.replace("çarpı","*").replace("bölü","/")
    s = s.replace(",",".")
    if "karekök" in s:
        n = re.findall(r"\d+\.?\d*", s)
        if n: return f"√{n[0]} = {math.sqrt(float(n[0])):.4f}"
    if "faktoriyel" in s:
        n = re.findall(r"\d+", s)
        if n and int(n[0])<=20: return f"{n[0]}! = {math.factorial(int(n[0]))}"
    if "sin" in s:
        n = re.findall(r"\d+\.?\d*", s)
        if n: return f"sin({n[0]}°) = {math.sin(math.radians(float(n[0]))):.4f}"
    if "cos" in s:
        n = re.findall(r"\d+\.?\d*", s)
        if n: return f"cos({n[0]}°) = {math.cos(math.radians(float(n[0]))):.4f}"
    if "tan" in s:
        n = re.findall(r"\d+\.?\d*", s)
        if n: return f"tan({n[0]}°) = {math.tan(math.radians(float(n[0]))):.4f}"
    if "pisagor" in s:
        n = re.findall(r"\d+\.?\d*", s)
        if len(n)>=2: return f"c = {math.sqrt(float(n[0])**2+float(n[1])**2):.4f}"
    if "yüzde" in s or "%" in s:
        n = re.findall(r"\d+\.?\d*", s)
        if len(n)>=2: return f"%{n[0]} × {n[1]} = {float(n[0])*float(n[1])/100:.2f}"
    if "ortalama" in s:
        n = re.findall(r"\d+\.?\d*", s)
        if n:
            nums = [float(x) for x in n]
            return f"Ortalama = {sum(nums)/len(nums):.2f}"
    try:
        ifade = re.sub(r"[^0-9+\-*/().**]","",s).strip()
        if ifade and len(ifade)>1:
            return f"{ifade} = {eval(ifade)}"
    except:
        pass
    return None

def cevap_uret(mesaj):
    m = mesaj.lower().strip()

    # 1. Hava durumu
    if "hava" in m:
        sehirler = ["istanbul","ankara","izmir","bursa","antalya","adana",
                    "konya","gaziantep","kayseri","trabzon","samsun",
                    "eskişehir","mersin","diyarbakır","erzurum","van",
                    "malatya","manisa","kocaeli","şanlıurfa"]
        for sehir in sehirler:
            if sehir in m:
                sonuc = hava_durumu(sehir)
                if sonuc: return "🌤️ Hava Durumu", sonuc
        sonuc = hava_durumu("Istanbul")
        if sonuc: return "🌤️ Hava Durumu", sonuc

    # 2. Döviz
    if any(k in m for k in ["dolar","euro","döviz","kur","usd","eur","sterlin","gbp"]):
        sonuc = doviz_kuru(m)
        if sonuc: return "💱 Güncel Kurlar", sonuc

    # 3. Matematik
    matematik_k = ["+","*","/","karekök","sin","cos","tan","pisagor",
                   "yüzde","%","faktoriyel","artı","çarpı","bölü","ortalama"]
    if any(k in m for k in matematik_k) or (re.search(r"\d",m) and len(m)<40):
        sonuc = matematik_coz(mesaj)
        if sonuc: return "🔢 Sonuç", sonuc

    # 4. Wikipedia — soruyu analiz edip anahtar kelime çıkar
    anahtar = soru_analiz(mesaj)
    if len(anahtar) > 1:
        baslik, icerik = wikipedia_ara(anahtar)
        if icerik:
            return f"📖 {baslik}", icerik

    return None, "Bu konuda bilgi bulamadım. Daha açık sorabilir misin?"

# ============================================================
# UI
# ============================================================
if "sohbet" not in st.session_state:
    st.session_state.sohbet = []

for msg in st.session_state.sohbet:
    with st.chat_message(msg["rol"]):
        if msg.get("baslik"):
            st.subheader(msg["baslik"])
        st.write(msg["icerik"])

if mesaj := st.chat_input("Bir şey sor..."):
    with st.chat_message("user"):
        st.write(mesaj)
    st.session_state.sohbet.append({"rol":"user","icerik":mesaj})

    with st.chat_message("assistant"):
        with st.spinner("Araştırıyor..."):
            baslik, yanit = cevap_uret(mesaj)
            if baslik:
                st.subheader(baslik)
            st.write(yanit)

    st.session_state.sohbet.append({
        "rol":"assistant",
        "baslik": baslik,
        "icerik": yanit
    })
