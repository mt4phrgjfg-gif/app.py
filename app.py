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

# --- 1. SİSTEM KONFİGÜRASYONU VE ARAYÜZ ---
st.set_page_config(page_title="Asistan Prime v30.5: OMNI-GENESIS", layout="wide", initial_sidebar_state="expanded")

# Ultra-Modern Cyberpunk Arayüz
st.markdown("""
    <style>
    .stApp { background: #010409; color: #58a6ff; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; }
    .stChatMessage { border: 1px solid #30363d; background: #0d1117; border-radius: 12px; margin-bottom: 10px; }
    .stSidebar { background-color: #0d1117 !important; border-right: 1px solid #30363d; }
    .metric-card { background: rgba(88, 166, 255, 0.05); padding: 15px; border-radius: 10px; border: 1px solid #30363d; text-align: center; }
    .status-active { color: #238636; font-weight: bold; text-shadow: 0 0 5px #238636; }
    </style>
    """, unsafe_allow_html=True)

HAFIZA_DOSYASI = "prime_brain.json"

# --- 2. ÇEKİRDEK FONKSİYONLAR (HAFIZA VE VERİ) ---

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

# --- 3. İLERİ NESİL ANALİZ MODÜLLERİ ---

# [v27.0] Neural Stress & Heavy Math
def mandelbrot_fractal(size=400):
    x, y = np.ogrid[-2:1:size*1j, -1.5:1.5:size*1j]
    c = x + 1j*y
    z = c
    for i in range(50): z = z**2 + c
    return z.real

# [v27.5] Kaos Teorisi (Lorenz Attractor)
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

# [v30.0] Strateji Grafiği (Graph Theory)
def strateji_agi_ciz():
    G = nx.DiGraph()
    G.add_edges_from([("Enerji", "Robot"), ("Güneş", "Enerji"), ("Robot", "Krater"), ("Krater", "Su"), ("Su", "Yaşam")])
    fig, ax = plt.subplots(figsize=(6, 4))
    nx.draw(G, nx.spring_layout(G), with_labels=True, node_color='#238636', edge_color='#58a6ff', font_color='white', ax=ax)
    fig.patch.set_facecolor('#0d1117')
    ax.set_facecolor('#0d1117')
    return fig

# [v30.0] Dinamik Kod Üretimi (Self-Mutation)
def kod_mutasyonu_uret(sorun):
    if "hız" in sorun or "yavaş" in sorun:
        return "

# --- 4. ANA DÖNGÜ VE KULLANICI DENEYİMİ ---

if "brain" not in st.session_state: st.session_state.brain = beyni_yukle()
if "messages" not in st.session_state: st.session_state.messages = []
if "last_viz" not in st.session_state: st.session_state.last_viz = None

# Sidebar: Sistem Monitörü
with st.sidebar:
    st.header("💠 OMNI-CORE V30.5")
    st.markdown(f"**Hafıza Ünitesi:** `{len(st.session_state.brain)}` Kavram")
    st.markdown("**Neural Engine:** <span class='status-active'>AKTİF</span>", unsafe_allow_html=True)
    st.markdown("**Termal Durum:** <span class='status-active'>OPTIMAL</span>", unsafe_allow_html=True)
    st.write("---")
    if st.button("Hafızayı Senkronize Et"):
        st.session_state.brain = beyni_yukle()
        st.toast("Hafıza güncellendi!")

# Ana Ekran
st.title("🦉 Asistan Prime: Omni-Genesis")
col_chat, col_dash = st.columns([1, 1.2])

with col_chat:
    st.subheader("📟 Terminal")
    chat_container = st.container(height=550)
    for m in st.session_state.messages:
        chat_container.chat_message(m["role"]).write(m["content"])

with col_dash:
    st.subheader("🔬 Genesis Dashboard")
    tab_strat, tab_math, tab_robot = st.tabs(["Strateji Ağı", "Kuantum/Kaos", "Robotik Kontrol"])
    
    with tab_strat:
        st.pyplot(strateji_agi_ciz())
    
    with tab_math:
        c1, c2 = st.columns(2)
        with c1: 
            if st.button("Kaos Analizi (Lorenz)"):
                st.session_state.last_viz = ("lorenz", lorenz_attractor())
        with c2:
            if st.button("Fraktal Stress Test"):
                st.session_state.last_viz = ("fractal", mandelbrot_fractal())
        
        if st.session_state.last_viz:
            v_type, v_data = st.session_state.last_viz
            if v_type == "lorenz": st.pyplot(v_data)
            else: 
                fig, ax = plt.subplots()
                ax.imshow(v_data, cmap='magma')
                plt.axis('off')
                st.pyplot(fig)

    with tab_robot:
        st.write("🛰️ **Spike Prime Gerçek Zamanlı Telemetri**")
        gyro = st.slider("Jiroskop", -180, 180, 0)
        st.progress(abs(gyro)/180, f"Denge Sapması: {gyro}°")
        if st.button("Keşif Başlat"):
            st.info(f"Otonom Tanımlama: {random.choice(['Buzul %92', 'Bazalt %14', 'Su %88'])}")

# KOMUT İŞLEME
if prompt := st.chat_input("Komut ver (Örn: 'Robot yavaşladı', 'Kaos analizi yap', 'X : Y öğret')"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    p_l = prompt.lower()
    
    with st.status("🧠 Omni-Core İşliyor...", expanded=False) as s:
        # 1. ÖĞRETME MODU
        if ":" in prompt:
            key, val = prompt.split(":", 1)
            st.session_state.brain[key.strip().lower()] = val.strip()
            beyni_guncelle(st.session_state.brain)
            response = f"✅ **Hafıza Güncellendi:** '{key.strip()}' bilgisi kalıcı hale getirildi."
        
        # 2. DİNAMİK KOD MODU
        elif any(x in p_l for x in ["yavaş", "hız", "motor", "hata"]):
            code = kod_mutasyonu_uret(p_l)
            response = f"🛠️ **Otonom Kod Üretimi:** Sorun tespit edildi, sistem kendini optimize ediyor:\n{code}"
        
        # 3. İLERİ ANALİZ TETİKLEYİCİ
        elif "kaos" in p_l or "fractal" in p_l or "matematik" in p_l:
            response = "🌀 **İleri Analiz:** Matematiksel motor tetiklendi. Sonuçları Dashboard 'Kuantum/Kaos' sekmesinde görebilirsiniz."
        
        # 4. HAFIZA SORGULAMA
        else:
            ans = None
            for k, v in st.session_state.brain.items():
                if k in p_l:
                    ans = v
                    break
            if ans: response = f"💡 **Hafıza Kaydı:** {ans}"
            else: response = "⚠️ Bilgi bulunamadı. Öğretmek için 'Konu : Açıklama' yazabilirsiniz."
        
        time.sleep(0.4)
        s.update(label="İşlem Tamamlandı!", state="complete")
    
    st.session_state.messages.append({"role": "assistant", "content": response})
    st.rerun()


