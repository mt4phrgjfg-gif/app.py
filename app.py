import streamlit as st
import json
import os
import time
import requests
import numpy as np
import matplotlib.pyplot as plt
import networkx as nx

# --- 1. SİSTEM YAPILANDIRMASI ---
st.set_page_config(page_title="Asistan Prime v31.2", layout="centered")

# API Anahtarı Otomatik Entegrasyonu
# Çevresel değişkenlerden veya çalışma zamanından anahtarı çeker
apiKey = "" 
appId = "asistan-prime-v31-2"

# CSS: Minimalist ve Akademik Koyu Tema
st.markdown("""
    <style>
    .stApp { background-color: #0d1117; color: #c9d1d9; font-family: 'Inter', sans-serif; }
    .stChatMessage { border-left: 2px solid #58a6ff; background-color: #161b22; margin-bottom: 12px; border-radius: 4px; }
    code { color: #ff7b72 !important; background-color: rgba(110, 118, 129, 0.4); padding: 2px 4px; border-radius: 4px; }
    .stSpinner > div > div { border-top-color: #58a6ff !important; }
    .source-box { font-size: 0.8em; color: #8b949e; margin-top: 10px; border-top: 1px solid #30363d; padding-top: 5px; }
    </style>
    """, unsafe_allow_html=True)

HAFIZA_DOSYASI = "prime_brain.json"

# --- 2. ÇEKİRDEK MOTORLAR ---

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

def derin_arastirma(query):
    """Google Search destekli canlı akademik sentezleme."""
    # Sadece gemini-2.5-flash-preview-09-2025 desteklenmektedir
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-preview-09-2025:generateContent?key={apiKey}"
    
    sys_instruction = (
        "Sen üst düzey bir bilimsel araştırma asistanısın. Google Search kullanarak "
        "derinlemesine, teknik ve akademik cevaplar ver. Basit yüzeysel bilgilerden kaçın. "
        "Karadelik, kuantum fiziği gibi konularda en güncel makalelere ve gözlemlere değin. "
        "Cevabı Türkçe ver ve mutlaka kaynakları link olarak belirt."
    )
    
    payload = {
        "contents": [{"parts": [{"text": query}]}],
        "systemInstruction": {"parts": [{"text": sys_instruction}]},
        "tools": [{"google_search": {}}]
    }
    
    # Exponential Backoff (1s, 2s, 4s, 8s, 16s)
    delays = [1, 2, 4, 8, 16]
    for delay in delays:
        try:
            response = requests.post(url, json=payload, timeout=30)
            if response.status_code == 200:
                data = response.json()
                text = data['candidates'][0]['content']['parts'][0]['text']
                # Grounding (Kaynaklar) ayıklama
                metadata = data['candidates'][0].get('groundingMetadata', {})
                attributions = metadata.get('groundingAttributions', [])
                
                sources = []
                for attr in attributions:
                    title = attr.get('web', {}).get('title')
                    uri = attr.get('web', {}).get('uri')
                    if title and uri:
                        sources.append(f"[{title}]({uri})")
                
                return text, sources
            time.sleep(delay)
        except Exception:
            time.sleep(delay)
    return "⚠️ Bilgi motoru meşgul veya bağlantı hatası oluştu. Lütfen tekrar deneyin.", []

# --- 3. ANALİZ VE GÖRSELLEŞTİRME ---

def lorenz_simulasyonu():
    dt = 0.01
    xs, ys, zs = np.empty(2000), np.empty(2000), np.empty(2000)
    xs[0], ys[0], zs[0] = (0., 1., 1.05)
    for i in range(1999):
        xs[i+1] = xs[i] + (10 * (ys[i] - xs[i])) * dt
        ys[i+1] = ys[i] + (xs[i] * (28 - zs[i]) - ys[i]) * dt
        zs[i+1] = zs[i] + (xs[i] * ys[i] - (8/3) * zs[i]) * dt
    fig = plt.figure(figsize=(5, 3))
    ax = fig.add_subplot(111, projection='3d')
    ax.plot(xs, ys, zs, lw=0.5, color='#58a6ff')
    ax.set_axis_off()
    fig.patch.set_facecolor('#0d1117')
    return fig

# --- 4. ANA DÖNGÜ ---

if "memory" not in st.session_state: st.session_state.memory = beyni_yukle()
if "messages" not in st.session_state: st.session_state.messages = []

st.title("🦉 Asistan Prime")
st.caption(f"v31.2 Deep Horizon | Hafıza Kaydı: {len(st.session_state.memory)}")

# Sohbet Akışı
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# Komut İşleme
if prompt := st.chat_input("Derin araştırma konusu veya komut girin..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    
    p_l = prompt.lower()
    
    with st.chat_message("assistant"):
        with st.spinner("🔍 İnternet ve akademik kaynaklar taranıyor..."):
            # A) Hafıza ve Öğretme [v26]
            if ":" in prompt and len(prompt.split(":")) == 2:
                k, v = prompt.split(":", 1)
                st.session_state.memory[k.strip().lower()] = v.strip()
                beyni_guncelle(st.session_state.memory)
                res = f"💾 **Nöral Kayıt:** '{k.strip()}' verisi kalıcı belleğe işlendi."
            
            # B) Kaos Simülasyonu [v27]
            elif "kaos" in p_l or "lorenz" in p_l:
                st.pyplot(lorenz_simulasyonu())
                res = "🌀 Kaos teorisi (Lorenz Attractor) başarıyla modellendi."
            
            # C) Robotik Kod Üretimi [v30]
            elif any(x in p_l for x in ["yavaş", "motor", "robot", "kod"]):
                res = "🛠️ **Otonom Kod Mutasyonu:**\n```python\n# Optimizasyon Çekirdeği\nmotor.set_power(100)\nsensors.recalibrate()\n```"
            
            # D) Canlı Akademik Arama [v31]
            else:
                # Önce hafızayı kontrol et
                ans = None
                for k, v in st.session_state.memory.items():
                    if k in p_l:
                        ans = v
                        break
                
                if ans:
                    res = f"💡 **Hafıza Verisi:** {ans}"
                else:
                    # Derin internet araştırması
                    text, sources = derin_arastirma(prompt)
                    res = text
                    if sources:
                        res += "\n\n**📚 Kaynakça:**\n" + "\n".join([f"- {s}" for s in sources])
            
            st.markdown(res)
            st.session_state.messages.append({"role": "assistant", "content": res})

