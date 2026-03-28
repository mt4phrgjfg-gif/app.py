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

