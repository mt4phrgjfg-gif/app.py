import streamlit as st
import json
import os
import time
import numpy as np
import matplotlib.pyplot as plt
import networkx as nx
import pandas as pd
import math

# --- 1. SİSTEM YAPILANDIRMASI (SADE TEMA) ---
st.set_page_config(page_title="Asistan Prime v30.5", layout="centered")

# CSS: Minimalist Koyu Tema
st.markdown("""
    <style>
    .stApp { background-color: #0d1117; color: #c9d1d9; font-family: 'Courier New', Courier, monospace; }
    .stChatMessage { background-color: #161b22; border: 1px solid #30363d; border-radius: 8px; padding: 10px; margin-bottom: 10px; }
    .stButton>button { background-color: #21262d; color: #c9d1d9; border: 1px solid #30363d; border-radius: 6px; }
    .stButton>button:hover { border-color: #58a6ff; }
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
    return {"sistem": "Omni-Genesis Çekirdeği Hazır."}

def beyni_guncelle(yeni_hafiza):
    with open(HAFIZA_DOSYASI, "w", encoding="utf-8") as f:
        json.dump(yeni_hafiza, f, ensure_ascii=False, indent=4)

def lorenz_attractor():
    dt = 0.01
    xs, ys, zs = np.empty(3000), np.empty(3000), np.empty(3000)
    xs[0], ys[0], zs[0] = (0., 1., 1.05)
    for i in range(2999):
        xs[i+1] = xs[i] + (10 * (ys[i] - xs[i])) * dt
        ys[i+1] = ys[i] + (xs[i] * (28 - zs[i]) - ys[i]) * dt
        zs[i+1] = zs[i] + (xs[i] * ys[i] - (8/3) * zs[i]) * dt
    fig = plt.figure(figsize=(5, 3))
    ax = fig.add_subplot(111, projection='3d')
    ax.plot(xs, ys, zs, lw=0.5, color='#58a6ff')
    ax.set_axis_off()
    fig.patch.set_facecolor('#0d1117')
    return fig

def strateji_agi():
    G = nx.DiGraph()
    G.add_edges_from([("Enerji", "Robot"), ("Güneş", "Enerji"), ("Robot", "Hedef")])
    fig, ax = plt.subplots(figsize=(5, 3))
    nx.draw(G, nx.spring_layout(G), with_labels=True, node_color='#238636', edge_color='#58a6ff', font_color='white', ax=ax)
    fig.patch.set_facecolor('#0d1117')
    ax.set_facecolor('#0d1117')
    return fig

# --- 3. ANA DÖNGÜ ---

if "brain" not in st.session_state: st.session_state.brain = beyni_yukle()
if "messages" not in st.session_state: st.session_state.messages = []

st.title("🦉 Asistan Prime")
st.caption(f"v30.5 Omni-Genesis | Hafıza Kapasitesi: {len(st.session_state.brain)}")

# Mesaj Geçmişi
chat_placeholder = st.container()
for msg in st.session_state.messages:
    chat_placeholder.chat_message(msg["role"]).write(msg["content"])

# Giriş ve Analiz
if prompt := st.chat_input("Komutunuzu yazın..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    p_l = prompt.lower()
    
    with st.spinner("⏳ Analiz Ediliyor..."):
        # 1. ÖĞRETME
        if ":" in prompt:
            key, val = prompt.split(":", 1)
            st.session_state.brain[key.strip().lower()] = val.strip()
            beyni_guncelle(st.session_state.brain)
            res = f"Bilgi hafızaya eklendi: **{key.strip()}**"
        
        # 2. KAOS/STRATEJİ ANALİZİ
        elif "kaos" in p_l or "plan" in p_l:
            st.pyplot(lorenz_attractor() if "kaos" in p_l else strateji_agi())
            res = "Matematiksel modelleme görselleştirildi."
        
        # 3. KOD MUTASYONU
        elif any(x in p_l for x in ["yavaş", "hız", "motor"]):
            res = "🛠️ **Otonom Kod Güncellemesi:**\n```python\nmotor.set_speed(100)\nsensors.sync()\n```"
            
        # 4. HAFIZA SORGULAMA
        else:
            res = "⚠️ Bilgi bulunamadı. Öğretmek için 'Konu : Açıklama' yazın."
            for k, v in st.session_state.brain.items():
                if k in p_l:
                    res = v
                    break
                    
    st.session_state.messages.append({"role": "assistant", "content": res})
    st.rerun()

