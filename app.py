import streamlit as st
import json
import os
import time
import requests
import numpy as np
import matplotlib.pyplot as plt
import networkx as nx
import math

# --- 1. SYSTEM CONFIGURATION ---
st.set_page_config(page_title="Asistan Prime v31.0", layout="wide")

# API Keys & IDs
apiKey = "" # Otomatik sağlanır
appId = "asistan-prime-v31-0"

# CSS: Professional Academic Dark Mode
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600&family=Fira+Code:wght@400;500&display=swap');
    .stApp { background-color: #0d1117; color: #c9d1d9; font-family: 'Inter', sans-serif; }
    .stChatMessage { border-left: 4px solid #58a6ff; background-color: #161b22; border-radius: 4px; margin-bottom: 20px; }
    code { font-family: 'Fira Code', monospace !important; color: #ff7b72 !important; }
    .source-box { background: #010409; padding: 10px; border: 1px solid #30363d; border-radius: 6px; font-size: 0.85em; margin-top: 10px; }
    .stButton>button { width: 100%; border-radius: 4px; background-color: #21262d; color: #c9d1d9; border: 1px solid #30363d; }
    .stButton>button:hover { border-color: #58a6ff; color: #58a6ff; }
    </style>
    """, unsafe_allow_html=True)

HAFIZA_DOSYASI = "prime_brain.json"

# --- 2. CORE ENGINES ---

# [v26] Memory Engine
def load_memory():
    if os.path.exists(HAFIZA_DOSYASI):
        try:
            with open(HAFIZA_DOSYASI, "r", encoding="utf-8") as f:
                return json.load(f)
        except: return {}
    return {"sistem": "Omni-Intelligence Core v31.0 Online."}

def save_memory(memory):
    with open(HAFIZA_DOSYASI, "w", encoding="utf-8") as f:
        json.dump(memory, f, ensure_ascii=False, indent=4)

# [v31] Academic Grounding Engine (Google Search)
def academic_query(query):
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-preview-09-2025:generateContent?key={apiKey}"
    
    system_prompt = (
        "You are an elite scientific research assistant. Provide deep, academic, and technical "
        "responses using provided search grounding. Avoid shallow explanations. If asked about "
        "physics or space, use formulas and refer to specific missions (e.g., Event Horizon Telescope, James Webb). "
        "Always cite your sources clearly at the end. Use Turkish for the final output."
    )
    
    payload = {
        "contents": [{"parts": [{"text": query}]}],
        "systemInstruction": {"parts": [{"text": system_prompt}]},
        "tools": [{"google_search": {}}]
    }
    
    # Exponential Backoff for stability
    for delay in [1, 2, 4]:
        try:
            response = requests.post(url, json=payload, timeout=30)
            if response.status_code == 200:
                result = response.json()
                text = result['candidates'][0]['content']['parts'][0]['text']
                grounding = result['candidates'][0].get('groundingMetadata', {}).get('groundingAttributions', [])
                sources = [f"[{s['web']['title']}]({s['web']['uri']})" for s in grounding if 'web' in s]
                return text, sources
            time.sleep(delay)
        except:
            time.sleep(delay)
    return "Bilgi motoru şu an meşgul. Lütfen yerel hafızayı sorgulayın.", []

# [v27/v30] Visual & Engineering Modules
def generate_fractal(size=300):
    x, y = np.ogrid[-2:1:size*1j, -1.5:1.5:size*1j]
    c = x + 1j*y
    z = c
    for _ in range(30): z = z**2 + c
    return z.real

def generate_strategy_graph():
    G = nx.DiGraph()
    G.add_edges_from([("Gözlem", "Veri"), ("Veri", "Analiz"), ("Analiz", "Hipotez"), ("Hipotez", "Yayın")])
    fig, ax = plt.subplots(figsize=(5, 3))
    nx.draw(G, nx.spring_layout(G), with_labels=True, node_color='#238636', edge_color='#58a6ff', font_color='white', ax=ax)
    fig.patch.set_facecolor('#0d1117')
    ax.set_facecolor('#0d1117')
    return fig

# --- 3. UI LAYOUT & MAIN LOOP ---

if "memory" not in st.session_state: st.session_state.memory = load_memory()
if "chat" not in st.session_state: st.session_state.chat = []

# Sidebar for controls
with st.sidebar:
    st.title("📟 Control Center")
    st.info(f"Hafıza Hücresi: {len(st.session_state.memory)}")
    if st.button("Hafızayı Senkronize Et"):
        st.session_state.memory = load_memory()
        st.success("Hafıza yüklendi.")
    st.write("---")
    st.subheader("🛠️ Lab Araçları")
    if st.button("Fraktal Stress Test"):
        st.session_state.chat.append({"role": "assistant", "type": "plot", "content": generate_fractal()})
    if st.button("Strateji Ağı Çiz"):
        st.session_state.chat.append({"role": "assistant", "type": "graph", "content": generate_strategy_graph()})

st.title("🦉 Asistan Prime")
st.caption("Omni-Intelligence v31.0 | Google Search & Academic Grounding Etkin")

# Chat Display
chat_area = st.container()
with chat_area:
    for m in st.session_state.chat:
        with st.chat_message(m["role"]):
            if m.get("type") == "plot":
                fig, ax = plt.subplots()
                ax.imshow(m["content"], cmap='magma')
                plt.axis('off')
                st.pyplot(fig)
            elif m.get("type") == "graph":
                st.pyplot(m["content"])
            else:
                st.markdown(m["content"])

# Input Logic
if prompt := st.chat_input("Bir soru sorun veya 'Konu : Bilgi' şeklinde öğretin..."):
    st.session_state.chat.append({"role": "user", "content": prompt})
    p_l = prompt.lower()
    
    with st.chat_message("assistant"):
        with st.spinner("🧠 Derin Analiz Yapılıyor..."):
            # 1. Memory Teaching [v26]
            if ":" in prompt and len(prompt.split(":")) == 2:
                k, v = prompt.split(":", 1)
                st.session_state.memory[k.strip().lower()] = v.strip()
                save_memory(st.session_state.memory)
                res = f"✅ **Hafıza Kaydı Başarılı:** '{k.strip()}' verisi nöral ağlara işlendi."
            
            # 2. Dynamic Code Gen [v30]
            elif any(x in p_l for x in ["yavaş", "motor", "robot", "hız"]):
                res = "🛠️ **Otonom Kod Optimizasyonu:**\n```python\n# Robotik Parametreler Güncellendi\nmotor.set_power(100)\nsensors.calibrate_gyro()\n```"
            
            # 3. Academic Search [v31]
            else:
                # Önce hafızaya bak
                ans = None
                for k, v in st.session_state.memory.items():
                    if k in p_l:
                        ans = v
                        break
                
                if ans:
                    res = f"💡 **Yerel Hafıza Verisi:** {ans}\n\n*Daha derin akademik analiz isterseniz 'Araştır:' komutunu kullanın.*"
                else:
                    # Hafızada yoksa veya "araştır" dendiyse internete sor
                    text, sources = academic_query(prompt)
                    res = text
                    if sources:
                        res += "\n\n**📚 Akademik Kaynaklar:**\n" + "\n".join([f"- {s}" for s in sources])
            
            st.markdown(res)
            st.session_state.chat.append({"role": "assistant", "content": res})
    st.rerun()

