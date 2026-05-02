import streamlit as st
import torch
import json
import re
import math
import requests
from transformers import AutoTokenizer, AutoModelForCausalLM

st.set_page_config(page_title="Prime Brain", page_icon="🧠")
st.title("🧠 Prime Brain")

@st.cache_resource
def model_yukle():
    MODEL = "ytu-ce-cosmos/turkish-gpt2"
    tokenizer = AutoTokenizer.from_pretrained(MODEL)
    model = AutoModelForCausalLM.from_pretrained(MODEL)
    tokenizer.pad_token = tokenizer.eos_token
    return tokenizer, model

tokenizer, model = model_yukle()

# ============================================================
# KAYNAKLAR — SADECE GÜVENİLİR SİTELER
# ============================================================

def wikipedia_ara(sorgu):
    try:
        # Önce Türkçe dene
        url = f"https://tr.wikipedia.org/api/rest_v1/page/summary/{requests.utils.quote(sorgu)}"
        r = requests.get(url, timeout=5, headers={"User-Agent": "PrimeBrain/1.0"})
        if r.status_code == 200:
            data = r.json()
            ozet = data.get("extract", "")
            if ozet and len(ozet) > 50:
                return f"📖 Wikipedia: {ozet[:600]}"
        # Türkçe bulunamazsa arama yap
        arama_url = f"https://tr.wikipedia.org/w/api.php?action=search&list=search&srsearch={requests.utils.quote(sorgu)}&format=json&srlimit=1"
        r2 = requests.get(arama_url, timeout=5)
        if r2.status_code == 200:
            data2 = r2.json()
            sonuclar = data2.get("query", {}).get("search", [])
            if sonuclar:
                baslik = sonuclar[0]["title"]
                url2 = f"https://tr.wikipedia.org/api/rest_v1/page/summary/{requests.utils.quote(baslik)}"
                r3 = requests.get(url2, timeout=5)
                if r3.status_code == 200:
                    ozet = r3.json().get("extract", "")
                    if ozet:
                        return f"📖 Wikipedia ({baslik}): {ozet[:600]}"
    except:
        pass
    return None

def hava_durumu(sehir):
    try:
        url = f"https://wttr.in/{requests.utils.quote(sehir)}?format=3"
        r = requests.get(url, timeout=5)
        if r.status_code == 200:
            return f"🌤️ {r.text.strip()}"
    except:
        pass
    return None

def doviz_kuru(para):
    try:
        url = "https://api.exchangerate-api.com/v4/latest/USD"
        r = requests.get(url, timeout=5)
        if r.status_code == 200:
            rates = r.json()["rates"]
            tl = rates.get("TRY", 0)
            eur_usd = rates.get("EUR", 0)
            if "euro" in para or "eur" in para:
                return f"💱 1 EUR = {tl/eur_usd:.2f} TL"
            if "dolar" in para or "usd" in para:
                return f"💱 1 USD = {tl:.2f} TL"
            return f"💱 1 USD = {tl:.2f} TL | 1 EUR = {tl/eur_usd:.2f} TL"
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
        if len(n)>=2: return f"c = √({n[0]}²+{n[1]}²) = {math.sqrt(float(n[0])**2+float(n[1])**2):.4f}"
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
        if ifade: return f"{ifade} = {eval(ifade)}"
    except:
        pass
    return None

def sohbet_et(mesaj, gecmis):
    giris = "\n".join(gecmis[-4:]) + f"\nKullanici: {mesaj}\nPrimeBrain:"
    inputs = tokenizer.encode(giris, return_tensors="pt", max_length=512, truncation=True)
    with torch.no_grad():
        outputs = model.generate(
            inputs, max_new_tokens=80, temperature=0.7,
            top_p=0.9, top_k=50, repetition_penalty=1.3,
            do_sample=True, pad_token_id=tokenizer.eos_token_id
        )
    yanit = tokenizer.decode(outputs[0], skip_special_tokens=True)
    yanit = yanit.split("PrimeBrain:")[-1].strip()
    yanit = yanit.split("Kullanici:")[0].strip()
    return yanit if yanit else "Bunu anlayamadım, tekrar sorar mısın?"

def akilli_cevap(mesaj):
    m = mesaj.lower()
    
    # Hava durumu
    if "hava" in m:
        sehirler = ["istanbul","ankara","izmir","bursa","antalya",
                    "adana","konya","gaziantep","kayseri","trabzon",
                    "samsun","eskişehir","kocaeli","mersin","diyarbakır"]
        for sehir in sehirler:
            if sehir in m:
                return hava_durumu(sehir)
        return hava_durumu("Istanbul")
    
    # Döviz
    if any(k in m for k in ["dolar","euro","döviz","kur","usd","eur","sterlin"]):
        return doviz_kuru(m)
    
    # Matematik
    matematik_kelimeler = ["+","-","*","/","karekök","sin","cos","tan",
                           "pisagor","yüzde","%","faktoriyel","artı",
                           "eksi","çarpı","bölü","ortalama"]
    if any(k in m for k in matematik_kelimeler) or (re.search(r"\d",m) and len(m)<40):
        sonuc = matematik_coz(mesaj)
        if sonuc:
            return f"🔢 {sonuc}"
    
    # Wikipedia — nedir/kimdir/ne demek soruları
    if any(k in m for k in ["nedir","kimdir","ne demek","hakkında","anlat","açıkla","kaç","tarih"]):
        temiz = re.sub(r"(nedir|kimdir|ne demek|hakkında|anlat|açıkla|\?)", "", m).strip()
        if temiz:
            sonuc = wikipedia_ara(temiz)
            if sonuc:
                return sonuc
    
    # Genel Wikipedia araması
    if len(mesaj) > 3:
        sonuc = wikipedia_ara(mesaj)
        if sonuc:
            return sonuc
    
    return None

# ============================================================
# UI
# ============================================================
if "gecmis" not in st.session_state:
    st.session_state.gecmis = []
if "sohbet" not in st.session_state:
    st.session_state.sohbet = []

st.caption("Wikipedia • Hava Durumu • Döviz • Matematik • Sohbet")

for msg in st.session_state.sohbet:
    with st.chat_message(msg["rol"]):
        st.write(msg["icerik"])

if mesaj := st.chat_input("Bir şey sor..."):
    with st.chat_message("user"):
        st.write(mesaj)
    st.session_state.sohbet.append({"rol":"user","icerik":mesaj})

    with st.chat_message("assistant"):
        with st.spinner("Düşünüyor..."):
            yanit = akilli_cevap(mesaj)
            if yanit:
                st.info(yanit)
            else:
                yanit = sohbet_et(mesaj, st.session_state.gecmis)
                st.write(yanit)
            st.session_state.gecmis.append(f"Kullanici: {mesaj}")
            st.session_state.gecmis.append(f"PrimeBrain: {yanit}")

    st.session_state.sohbet.append({"rol":"assistant","icerik":yanit})
