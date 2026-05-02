import streamlit as st
import torch
import json
import re
import math
from transformers import AutoTokenizer, AutoModelForCausalLM

st.set_page_config(page_title="Prime Brain", page_icon="🧠")
st.title("🧠 Prime Brain — Sohbet & Matematik AI")

@st.cache_resource
def model_yukle():
    MODEL = "ytu-ce-cosmos/turkish-gpt2"
    tokenizer = AutoTokenizer.from_pretrained(MODEL)
    model = AutoModelForCausalLM.from_pretrained(MODEL)
    tokenizer.pad_token = tokenizer.eos_token
    return tokenizer, model

tokenizer, model = model_yukle()

def matematik_coz(soru):
    soru = soru.lower()
    soru = soru.replace("artı","+").replace("eksi","-")
    soru = soru.replace("çarpı","*").replace("bölü","/")
    soru = soru.replace(",",".")
    if "karekök" in soru:
        sayi = re.findall(r"\d+\.?\d*", soru)
        if sayi: return f"√{sayi[0]} = {math.sqrt(float(sayi[0])):.4f}"
    if "faktoriyel" in soru:
        sayi = re.findall(r"\d+", soru)
        if sayi: return f"{sayi[0]}! = {math.factorial(int(sayi[0]))}"
    if "sin" in soru:
        sayi = re.findall(r"\d+\.?\d*", soru)
        if sayi: return f"sin({sayi[0]}) = {math.sin(math.radians(float(sayi[0]))):.4f}"
    if "cos" in soru:
        sayi = re.findall(r"\d+\.?\d*", soru)
        if sayi: return f"cos({sayi[0]}) = {math.cos(math.radians(float(sayi[0]))):.4f}"
    if "pisagor" in soru:
        sayilar = re.findall(r"\d+\.?\d*", soru)
        if len(sayilar) >= 2:
            a,b = float(sayilar[0]),float(sayilar[1])
            return f"c = {math.sqrt(a**2+b**2):.4f}"
    if "yüzde" in soru or "%" in soru:
        sayilar = re.findall(r"\d+\.?\d*", soru)
        if len(sayilar) >= 2:
            return f"%{sayilar[0]} × {sayilar[1]} = {float(sayilar[0])*float(sayilar[1])/100:.2f}"
    try:
        ifade = re.sub(r"[^0-9+\-*/().**]", "", soru).strip()
        if ifade: return f"{ifade} = {eval(ifade)}"
    except:
        pass
    return None

def sohbet_et(mesaj, gecmis):
    giris = "\n".join(gecmis[-6:]) + f"\nKullanici: {mesaj}\nPrimeBrain:"
    inputs = tokenizer.encode(giris, return_tensors="pt", max_length=512, truncation=True)
    with torch.no_grad():
        outputs = model.generate(
            inputs, max_new_tokens=100, temperature=0.7,
            top_p=0.9, top_k=50, repetition_penalty=1.3,
            do_sample=True, pad_token_id=tokenizer.eos_token_id
        )
    yanit = tokenizer.decode(outputs[0], skip_special_tokens=True)
    yanit = yanit.split("PrimeBrain:")[-1].strip()
    yanit = yanit.split("Kullanici:")[0].strip()
    return yanit

# Sohbet geçmişi
if "gecmis" not in st.session_state:
    st.session_state.gecmis = []
if "sohbet" not in st.session_state:
    st.session_state.sohbet = []

# Geçmiş mesajları göster
for msg in st.session_state.sohbet:
    with st.chat_message(msg["rol"]):
        st.write(msg["icerik"])

# Kullanıcı girişi
if mesaj := st.chat_input("Bir şey sor veya matematik hesapla..."):
    with st.chat_message("user"):
        st.write(mesaj)
    st.session_state.sohbet.append({"rol": "user", "icerik": mesaj})

    matematik_kelimeler = ["+","-","*","/","karekök","sin","cos",
                           "pisagor","yüzde","%","faktoriyel","artı",
                           "eksi","çarpı","bölü"]
    is_matematik = any(k in mesaj.lower() for k in matematik_kelimeler)
    is_sayi = bool(re.search(r"\d", mesaj))

    with st.chat_message("assistant"):
        with st.spinner("Düşünüyor..."):
            if is_matematik or (is_sayi and len(mesaj) < 40):
                sonuc = matematik_coz(mesaj)
                yanit = sonuc if sonuc else "Bu işlemi anlayamadım."
                st.success(f"🔢 {yanit}")
            else:
                yanit = sohbet_et(mesaj, st.session_state.gecmis)
                st.write(yanit)
                st.session_state.gecmis.append(f"Kullanici: {mesaj}")
                st.session_state.gecmis.append(f"PrimeBrain: {yanit}")

    st.session_state.sohbet.append({"rol": "assistant", "icerik": yanit})
