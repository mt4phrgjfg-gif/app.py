import streamlit as st
import json
import os
import time
import random
import numpy as np
import matplotlib.pyplot as plt
import networkx as nx
import pandas as pd
from PIL import Image, ImageDraw
from scipy.spatial import ConvexHull
import math

# --- 1. SİSTEM YAPILANDIRMASI ---
st.set_page_config(page_title="Asistan Prime v30.5: OMNI-GENESIS", layout="wide")

# Görsel Stil Ayarları
st.markdown("""
    <style>
    .stApp { background: #010409; color: #58a6ff; }
    .stChatMessage { border: 1px solid #30363d; background: #0d1117; border-radius: 12px; }
    .status-active { color: #238636; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

HAFIZA_DOSYASI = "prime_brain.json"

# --- 2. HAFIZA YÖNETİMİ (v26 Mirası) ---
def beyni_yukle():
    if os.path.exists(HAFIZA_DOSYASI):
        try:
            with open(HAFIZA_DOSYASI, "r", encoding="utf-8") as f:
                return json.load(f)
        except: return {}
    return {"sistem": "Omni-Genesis Çekirdeği Aktif."}

def beyni_guncelle(yeni_hafiza):
    with open(HAFIZA_DOSYASI, "w", encoding="utf-8") as f:
        json.dump(yeni_hafiza, f, ensure_ascii=False, indent=4)

# --- 3. ANALİZ VE SİMÜLASYON MODÜLLERİ ---

def lorenz_attractor(iterasyon=5000):
    dt = 0.01
    xs, ys, zs = np.empty(iterasyon), np.empty(iterasyon), np.empty(iterasyon)
    xs[0], ys[0], zs[0] = (0., 1., 1.05)
    for i in range(iterasyon - 1):
        xs[i+1] = xs[i] + (10 * (ys[i] - xs[i])) * dt
        ys[i+1] = ys[i] + (xs[i] * (28 - zs[i]) - ys[i]) * dt
        zs[i+1] = zs[i] + (xs[i] * ys[i] - (8/3) * zs[i]) * dt
    fig = plt.figure(figsize=(6, 4))
    ax = fig.add_subplot(111, projection='3d')
    ax.plot(xs, ys, zs, lw=0.5, color='#ff00ff')
    ax.set_axis_off()
    fig.patch.set_facecolor('#0d1117')
    return fig

def strateji_agi_ciz():
    G = nx.DiGraph()
    G.add_edges_from([("Güneş", "Enerji"), ("Enerji", "Robot"), ("Robot", "Krater"), ("Krater", "Su")])
    fig, ax = plt.subplots(figsize=(6, 4))
    nx.draw(G, nx.spring_layout(G), with_labels=True, node_color='#238636', edge_color='#58a6ff', font_color='white', ax=ax)
    fig.patch.set_facecolor('#0d1117')
    ax.set_facecolor('#0d1117')
    return fig

def kod_mutasyonu_uret(sorun):
    if "yavaş" in sorun or "hız" in sorun:
        return "```python\n# Optimizasyon Modülü\nmotor.set_speed(100)\nprint('Hız Maksimuma Çıkarıldı')\n```"
    return "```python\n# Sistem Kontrolü\nsensors.sync()\n```"

# --- 4. ANA ARAYÜZ ---

if "brain" not in st.session_state: st.session_state.brain = beyni_yukle()
if "messages" not in st.session_state: st.session_state.messages = []

# Sidebar
with st.sidebar:
    st.header("💠 OMNI-CORE v30.5")
    st.write(f"Hafıza Hücresi: {len(st.session_state.brain)}")
    if st.button("Hafızayı Sıfırla"):
        st.session_state.brain = {"sistem": "Yeniden Başlatıldı"}
        beyni_guncelle(st.session_state.brain)
        st.rerun()

st.title("🦉 Asistan Prime: Omni-Genesis")

col_chat, col_dash = st.columns([1, 1.2])

with col_chat:
    st.subheader("📟 Terminal")
    chat_container = st.container(height=500)
    for m in st.session_state.messages:
        chat_container.chat_message(m["role"]).write(m["content"])

with col_dash:
    st.subheader("🔬 Dashboard")
    tab1, tab2 = st.tabs(["Strateji ve Kaos", "Robotik"])
    with tab1:
        st.pyplot(strateji_agi_ciz())
        if st.button("Kaos Analizi Başlat"):
            st.pyplot(lorenz_attractor())
    with tab2:
        gyro = st.slider("Jiroskop", -90, 90, 0)
        st.info(f"Denge Durumu: {'Stabil' if abs(gyro) < 20 else 'Kritik!'}")

# Komut Girişi
if prompt := st.chat_input("Komutunuzu buraya yazın..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    p_l = prompt.lower()
    
    if ":" in prompt:
        k, v = prompt.split(":", 1)
        st.session_state.brain[k.strip().lower()] = v.strip()
        beyni_guncelle(st.session_state.brain)
        res = "✅ Bilgi hafızaya kaydedildi."
    elif "yavaş" in p_l or "hız" in p_l:
        res = f"🛠️ Kod mutasyonu tamamlandı:\n{kod_mutasyonu_uret(p_l)}"
    else:
        res = "Bilgi bulunamadı. Lütfen 'Konu : Açıklama' şeklinde öğretin."
        for k, v in st.session_state.brain.items():
            if k in p_l:
                res = v
                break
                
    st.session_state.messages.append({"role": "assistant", "content": res})
    st.rerun()

