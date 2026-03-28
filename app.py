import streamlit as st
import json
import os
import time
import random

# --- 1. SİSTEM AYARLARI ---
st.set_page_config(page_title="Asistan Prime v26.0", page_icon="🚀", layout="wide")

# Hafıza Dosyası Kontrolü
HAFIZA_DOSYASI = "prime_brain.json"

def beyni_yukle():
    if os.path.exists(HAFIZA_DOSYASI):
        with open(HAFIZA_DOSYASI, "r", encoding="utf-8") as f:
            return json.load(f)
    return {
        "öğrenme": "Yapay sinir ağlarının veriden desen çıkarma sürecidir.",
        "nörosembolik": "Mantık ve derin öğrenmenin birleştiği en ileri yapay zeka mimarisidir.",
        "robotik": "Sensörler (Göz), Motorlar (Kas) ve Kodun (Beyin) mükemmel uyumudur."
    }

def beyni_guncelle(yeni_bilgi):
    with open(HAFIZA_DOSYASI, "w", encoding="utf-8") as f:
        json.dump(yeni_bilgi, f, ensure_ascii=False, indent=4)

# --- 2. ASİSTANIN KİŞİLİĞİ VE GÖRÜNÜMÜ ---
st.title("🚀 Asistan Prime v26.0: Ultra")
st.sidebar.header("⚙️ Sistem Durumu")
st.sidebar.success("Nöral Ağlar: Aktif")
st.sidebar.info("Mantık Katmanı: %100")

if "brain" not in st.session_state:
    st.session_state.brain = beyni_yukle()

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# --- 3. İLERİ DÜZEY MANTIK MOTORU (Nöro-Sembolik Yaklaşım) ---
def akilli_cevap_motoru(soru):
    soru = soru.lower().strip()
    
    # Adım 1: Chain of Thought (Düşünce Zinciri Simülasyonu)
    with st.status("🧠 Düşünce Zinciri Başlatıldı...", expanded=False) as s:
        time.sleep(0.4)
        st.write("🔍 Anahtar kavramlar analiz ediliyor...")
        time.sleep(0.4)
        st.write("📂 Hafıza katmanları taranıyor...")
        
        # Adım 2: Anlamsal Eşleşme (Semantic Match)
        bulunan_anahtar = None
        for anahtar in st.session_state.brain.keys():
            if anahtar in soru: # Basit ama etkili bir sembolik bağ
                bulunan_anahtar = anahtar
                break
        
        time.sleep(0.4)
        st.write("💡 Mantıksal çıkarım yapılıyor...")
        s.update(label="Analiz Tamamlandı!", state="complete")

    # Adım 3: Yanıt Oluşturma
    if bulunan_anahtar:
        return f"**Analizim Sonucu:** {st.session_state.brain[bulunan_anahtar]} \n\n*Başmühendis, bu konu hakkında başka bir derinleştirme yapalım mı?*"
    else:
        return "⚠️ Bu kavram nöral ağlarımda tanımlı değil. Bana öğretirsen, bir dahaki sefere bunu 'Düşünce Zinciri'me dahil edebilirim. \n\n**Öğretmek için:** `Konu : Açıklama` şeklinde yaz."

# --- 4. SOHBET ARAYÜZÜ ---
for chat in st.session_state.chat_history:
    with st.chat_message(chat["role"]):
        st.markdown(chat["content"])

if prompt := st.chat_input("Bir komut girin..."):
    st.session_state.chat_history.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # ÖĞRETME MODU (Sembolik Kayıt)
    if ":" in prompt:
        konu, aciklama = prompt.split(":", 1)
        st.session_state.brain[konu.strip().lower()] = aciklama.strip()
        beyni_guncelle(st.session_state.brain)
        response = f"✅ **Sistem Güncellendi.** '{konu.strip()}' kavramı kalıcı hafızaya alındı."
    else:
        # CEVAPLAMA MODU
        response = akilli_cevap_motoru(prompt)

    with st.chat_message("assistant"):
        st.markdown(response)
        st.session_state.chat_history.append({"role": "assistant", "content": response})
