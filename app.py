import streamlit as st
import json
import os
import time
import requests
import numpy as np

# --- 1. SİSTEM YAPILANDIRMASI ---
st.set_page_config(page_title="Asistan Prime v31.7", layout="centered")

# API Anahtarı: Sistem tarafından otomatik enjekte edilir, manuel giriş gerekmez.
apiKey = "" 

# Görsel Stil (Sade ve Akademik Terminal)
st.markdown("""
    <style>
    .stApp { background-color: #0d1117; color: #c9d1d9; font-family: 'Inter', sans-serif; }
    .stChatMessage { border-left: 2px solid #58a6ff; background-color: #161b22; margin-bottom: 10px; }
    code { color: #ff7b72 !important; }
    .source-box { font-size: 0.8em; color: #8b949e; margin-top: 5px; border-top: 1px solid #30363d; }
    </style>
    """, unsafe_allow_html=True)

HAFIZA_DOSYASI = "prime_brain.json"

# --- 2. ÇEKİRDEK FONKSİYONLAR ---

def beyni_yukle():
    if os.path.exists(HAFIZA_DOSYASI):
        try:
            with open(HAFIZA_DOSYASI, "r", encoding="utf-8") as f:
                return json.load(f)
        except: return {}
    return {"sistem": "Omni-Intelligence Aktif."}

def beyni_guncelle(yeni_hafiza):
    with open(HAFIZA_DOSYASI, "w", encoding="utf-8") as f:
        json.dump(yeni_hafiza, f, ensure_ascii=False, indent=4)

def akademik_sentez(query):
    """Sistemin yerleşik Gemini modelini Google Search ile kullanır."""
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-preview-09-2025:generateContent?key={apiKey}"
    
    payload = {
        "contents": [{"parts": [{"text": query}]}],
        "systemInstruction": {
            "parts": [{"text": "Sen Başmühendisin akademik asistanısın. Derin, teknik ve bilimsel konuş. Karadelik gibi konularda makale referansları ver. Türkçe cevap ver."}]
        },
        "tools": [{"google_search": {}}]
    }
    
    # Hata durumunda yeniden deneme (Exponential Backoff)
    for delay in [1, 2, 4]:
        try:
            response = requests.post(url, json=payload, timeout=30)
            if response.status_code == 200:
                result = response.json()
                text = result['candidates'][0]['content']['parts'][0]['text']
                # Kaynakları ayıkla
                sources = result['candidates'][0].get('groundingMetadata', {}).get('groundingAttributions', [])
                links = [f"[{s['web']['title']}]({s['web']['uri']})" for s in sources if 'web' in s]
                return text, links
            time.sleep(delay)
        except:
            time.sleep(delay)
    return "⚠️ Bilgi motoruna şu an ulaşılamıyor. Yerel hafıza aktif.", []

# --- 3. ANA DÖNGÜ ---

if "memory" not in st.session_state: st.session_state.memory = beyni_yukle()
if "history" not in st.session_state: st.session_state.history = []

st.title("🦉 Asistan Prime")
st.caption(f"v31.7 Native Core | Hafıza: {len(st.session_state.memory)} Kayıt")

# Sohbet Geçmişi
for msg in st.session_state.history:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# Giriş ve İşleme
if prompt := st.chat_input("Komut girin veya araştırma isteyin..."):
    st.session_state.history.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    
    p_l = prompt.lower()
    
    with st.chat_message("assistant"):
        with st.spinner("🧠 Analiz ediliyor..."):
            # 1. ÖĞRETME MODU [v26]
            if ":" in prompt and len(prompt.split(":")) == 2:
                k, v = prompt.split(":", 1)
                st.session_state.memory[k.strip().lower()] = v.strip()
                beyni_guncelle(st.session_state.memory)
                res = f"💾 **Hafıza Kaydı:** '{k.strip()}' verisi kalıcı belleğe işlendi."
            
            # 2. ROBOTİK KOD [v30]
            elif any(x in p_l for x in ["robot", "motor", "kod", "hız"]):
                res = "🛠️ **Otonom Kod Üretimi:**\n```python\nmotor.set_power(100)\npid.optimize(gain=1.5)\n```"
            
            # 3. AKADEMİK ARAŞTIRMA [v31]
            else:
                # Hafızada var mı?
                ans = None
                for k, v in st.session_state.memory.items():
                    if k in p_l:
                        ans = v
                        break
                
                if ans:
                    res = f"💡 **Hafıza:** {ans}"
                else:
                    # Yoksa internete sor (Native Google Search)
                    text, sources = akademik_sentez(prompt)
                    res = text
                    if sources:
                        res += "\n\n**📚 Kaynakça:**\n" + "\n".join([f"- {s}" for s in sources])
            
            st.markdown(res)
            st.session_state.history.append({"role": "assistant", "content": res})

