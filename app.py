import streamlit as st
import torch
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
# KAYNAKLAR
# ============================================================

def wikipedia_ara(sorgu):
    try:
        # 1. Direkt arama
        arama = f"https://tr.wikipedia.org/w/api.php?action=query&list=search&srsearch={requests.utils.quote(sorgu)}&format=json&srlimit=3"
        r = requests.get(arama, timeout=5, headers={"User-Agent": "PrimeBrain/1.0"})
        if r.status_code == 200:
            sonuclar = r.json().get("query", {}).get("search", [])
            for sonuc in sonuclar:
                baslik = sonuc["title"]
                ozet_url = f"https://tr.wikipedia.org/api/rest_v1/page/summary/{requests.utils.quote(baslik)}"
                r2 = requests.get(ozet_url, timeout=5)
                if r2.status_code == 200:
                    ozet = r2.json().get("extract", "")
                    if ozet and len(ozet) > 80:
                        return f"📖 **{baslik}**\n\n{ozet[:800]}"
    except:
        pass
    return None

def wikipedia_bolum_ara(sorgu):
    """Daha derin arama — birden fazla paragraf getirir"""
    try:
        arama = f"https://tr.wikipedia.org/w/api.php?action=query&list=search&srsearch={requests.utils.quote(sorgu)}&format=json&srlimit=1"
        r = requests.get(arama, timeout=5)
        if r.status_code == 200:
            sonuclar = r.json().get("query", {}).get("search", [])
            if sonuclar:
                baslik = sonuclar[0]["title"]
                icerik_url = f"https://tr.wikipedia.org/w/api.php?action=query&titles={requests.utils.quote(baslik)}&prop=extracts&exintro=true&format=json"
                r2 = requests.get(icerik_url, timeout=5)
                if r2.status_code == 200:
                    pages = r2.json().get("query", {}).get("pages", {})
                    for page in pages.values():
                        icerik = page.get("extract", "")
                        # HTML taglarını temizle
                        icerik = re.sub(r"<[^>]+>", "", icerik)
                        icerik = re.sub(r"\n+", "\n", icerik).strip()
                        if icerik:
                            return f"📖 **{baslik}**\n\n{icerik[:1000]}"
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
            eur = rates.get("EUR", 0)
            gbp = rates.get("GBP", 0)
            if "euro" in para or "eur" in para:
                return f"💱 1 EUR = {tl/eur:.2f} TL"
            if "sterlin" in para or "gbp" in para:
                return f"💱 1 GBP = {tl/gbp:.2f} TL"
            return f"💱 1 USD = {tl:.2f} TL | 1 EUR = {tl/eur:.2f} TL | 1 GBP = {tl/gbp:.2f} TL"
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
        if ifade and len(ifade)>1: return f"{ifade} = {eval(ifade)}"
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
    m = mesaj.lower().strip()

    # Hava durumu
    if "hava" in m:
        sehirler = ["istanbul","ankara","izmir","bursa","antalya","adana",
                    "konya","gaziantep","kayseri","trabzon","samsun",
                    "eskişehir","kocaeli","mersin","diyarbakır","erzurum",
                    "malatya","van","şanlıurfa","manisa"]
        for sehir in sehirler:
            if sehir in m:
                return hava_durumu(sehir)
        return hava_durumu("Istanbul")

    # Döviz
    if any(k in m for k in ["dolar","euro","döviz","kur","usd","eur","sterlin","gbp"]):
        return doviz_kuru(m)

    # Matematik
    matematik_kelimeler = ["+","-","*","/","karekök","sin","cos","tan",
                           "pisagor","yüzde","%","faktoriyel","artı",
                           "eksi","çarpı","bölü","ortalama"]
    if any(k in m for k in matematik_kelimeler) or (re.search(r"\d",m) and len(m)<40):
        sonuc = matematik_coz(mesaj)
        if sonuc:
            return f"🔢 {sonuc}"

    # Wikipedia — her türlü soru
    temiz = re.sub(r"(nedir|kimdir|ne demek|hakkında|anlat|açıkla|söyle|bilgi ver|\?)", "", m).strip()
    if len(temiz) > 2:
        # Önce derin arama dene
        sonuc = wikipedia_bolum_ara(temiz)
        if sonuc:
            return sonuc
        # Bulamazsa basit arama
        sonuc = wikipedia_ara(temiz)
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

st.caption("📖 850K+ Wikipedia konusu • 🌤️ Hava • 💱 Döviz • 🔢 Matematik • 💬 Sohbet")

for msg in st.session_state.sohbet:
    with st.chat_message(msg["rol"]):
        st.markdown(msg["icerik"])

if mesaj := st.chat_input("Bir şey sor..."):
    with st.chat_message("user"):
        st.write(mesaj)
    st.session_state.sohbet.append({"rol":"user","icerik":mesaj})

    with st.chat_message("assistant"):
        with st.spinner("Araştırıyor..."):
            yanit = akilli_cevap(mesaj)
            if yanit:
                st.markdown(yanit)
            else:
                yanit = sohbet_et(mesaj, st.session_state.gecmis)
                st.write(yanit)
            st.session_state.gecmis.append(f"Kullanici: {mesaj}")
            st.session_state.gecmis.append(f"PrimeBrain: {yanit}")

    st.session_state.sohbet.append({"rol":"assistant","icerik":yanit})
