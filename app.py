```python
import streamlit as st
import requests
from bs4 import BeautifulSoup
import json
import os
import numpy as np
import matplotlib.pyplot as plt
import networkx as nx
from io import BytesIO
from PIL import Image

# --- CORE ENGINE CONFIGURATION ---
# No API Keys. Pure algorithmic power and web scraping.
st.set_page_config(page_title="Prime Apex v33.1", layout="wide", initial_sidebar_state="expanded")
BRAIN_PATH = "prime_brain.json"

# Premium Dark Academic Theme
st.markdown("""
    <style>
    .stApp { background-color: #0d1117; color: #c9d1d9; font-family: 'JetBrains Mono', monospace; }
    .stChatMessage { border-bottom: 1px solid #30363d; background-color: #0d1117; padding: 20px; }
    .agent-tag { 
        color: #58a6ff; 
        font-size: 11px; 
        border: 1px solid #58a6ff; 
        padding: 2px 8px; 
        border-radius: 12px;
        text-transform: uppercase;
        font-weight: bold;
    }
    .stSidebar { background-color: #161b22; border-right: 1px solid #30363d; }
    code { color: #ff7b72 !important; background-color: #21262d !important; padding: 4px; border-radius: 4px; }
    </style>
    """, unsafe_allow_html=True)

# --- LAYER 1: NEURAL MEMORY & RAG (v26) ---
def sync_brain(action="load", data=None):
    if not os.path.exists(BRAIN_PATH):
        with open(BRAIN_PATH, "w", encoding="utf-8") as f:
            json.dump({"system_status": "Prime Active", "init_v": 33.1}, f)
    
    if action == "load":
        try:
            with open(BRAIN_PATH, "r", encoding="utf-8") as f:
                return json.load(f)
        except: return {}
    elif action == "save" and data:
        with open(BRAIN_PATH, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)

# --- LAYER 2: ACADEMIC SCRAPING ENGINE (v31) ---
def academic_engine(query):
    """
    Scrapes scientific data from secure headers. No API key required.
    Uses specialized headers to mimic a high-end research terminal.
    """
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko)"
    }
    # Targeted search for technical accuracy
    search_url = f"https://html.duckduckgo.com/html/?q={query.replace(' ', '+')}+physics+research+paper"
    
    try:
        response = requests.get(search_url, headers=headers, timeout=12)
        soup = BeautifulSoup(response.text, 'html.parser')
        snippets = soup.find_all('a', class_='result__snippet')
        
        if not snippets:
            return "🔍 Sistem Notu: Derin ağda doğrudan eşleşme bulunamadı. Teorik mantık yürütülüyor.", []
        
        raw_data = "\n\n".join([f"• {s.text}" for s in snippets[:4]])
        links = [a['href'] for a in soup.find_all('a', class_='result__url')][:4]
        return raw_data, links
    except Exception as e:
        return f"⚠️ Veri Hattı Kesildi: {str(e)}", []

# --- LAYER 3: DYNAMIC MATH & CHAOS (v27) ---
def generate_chaos_model():
    dt = 0.01
    num_steps = 2500
    xs, ys, zs = np.empty(num_steps), np.empty(num_steps), np.empty(num_steps)
    xs[0], ys[0], zs[0] = (0., 1., 1.05)
    
    for i in range(num_steps - 1):
        xs[i+1] = xs[i] + (10 * (ys[i] - xs[i])) * dt
        ys[i+1] = ys[i] + (xs[i] * (28 - zs[i]) - ys[i]) * dt
        zs[i+1] = zs[i] + (xs[i] * ys[i] - (8/3) * zs[i]) * dt
        
    fig = plt.figure(figsize=(6, 4))
    ax = fig.add_subplot(111, projection='3d')
    ax.plot(xs, ys, zs, lw=0.6, color='#58a6ff')
    ax.set_axis_off()
    fig.patch.set_facecolor('#0d1117')
    return fig

# --- LAYER 4: MULTIMODAL VISION MATRIX (v33) ---
def analyze_vision_matrix(uploaded_file):
    img = Image.open(uploaded_file)
    img_array = np.array(img.convert('RGB'))
    h, w, _ = img_array.shape
    
    # Calculate Complexity (Entropy proxy)
    brightness = np.mean(img_array, axis=2)
    complexity = np.std(brightness)
    
    return {
        "res": f"{w}x{h}",
        "density": np.mean(img_array),
        "entropy": complexity,
        "dominant_channel": ["Red", "Green", "Blue"][np.argmax(np.mean(img_array, axis=(0,1)))]
    }

# --- MAIN OPERATIONAL INTERFACE ---
def main():
    brain = sync_brain("load")
    
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Sidebar: System Diagnostics
    with st.sidebar:
        st.markdown("### 🛠️ PRIME DIAGNOSTICS")
        st.info(f"System: v33.1 (Apex)")
        st.write(f"Neural Points: {len(brain)}")
        
        st.markdown("---")
        st.write("**Vision Processing**")
        v_file = st.file_uploader("Sinyal/Görsel Yükle", type=["jpg", "png", "jpeg"])
        if v_file and st.button("Matrisi Çöz"):
            stats = analyze_vision_matrix(v_file)
            st.success(f"Analiz: {stats['res']} | Entropi: {stats['entropy']:.2f}")
            st.session_state.messages.append({
                "role": "assistant", 
                "tag": "VISION",
                "content": f"👁️ **Görsel Matris Çözümlendi:**\n- Çözünürlük: {stats['res']}\n- Baskın Kanal: {stats['dominant_channel']}\n- Teknik Yoğunluk: {stats['entropy']:.2f}"
            })

        if st.button("Lorenz Kaos Analizi"):
            st.session_state.messages.append({
                "role": "assistant", "tag": "MATH", "content": "Kaos modeli simüle edildi.", "type": "plot"
            })

    # Chat Feed
    for m in st.session_state.messages:
        with st.chat_message(m["role"]):
            if "tag" in m:
                st.markdown(f"<span class='agent-tag'>{m['tag']}</span>", unsafe_allow_html=True)
            st.markdown(m["content"])
            if m.get("type") == "plot":
                st.pyplot(generate_chaos_model())

    # Commander Input
    prompt = st.chat_input("Komut veya teknik analiz talebi...")

    if prompt:
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        p_low = prompt.lower()
        
        with st.chat_message("assistant"):
            # 1. MEMORY RECORDING (v26)
            if ":" in prompt and len(prompt.split(":")) == 2:
                key, val = prompt.split(":", 1)
                brain[key.strip().lower()] = val.strip()
                sync_brain("save", brain)
                msg = f"💾 Veri '{key.strip()}' nöral ağa kalıcı olarak işlendi."
                st.markdown(f"<span class='agent-tag'>MEMORY</span><br/><br/>{msg}", unsafe_allow_html=True)
                st.session_state.messages.append({"role": "assistant", "tag": "MEMORY", "content": msg})
            
            # 2. CODE/ROBOTICS AGENT (v30)
            elif any(x in p_low for x in ["robot", "kod", "motor", "python", "hata"]):
                code_res = """
```python
# Otonom Kontrol Modülü v33.1
def system_override():
    throttle = 1.0
    status = "OPTIMAL"
    return {"power": throttle, "status": status}

```
"""
st.markdown(f"<span class='agent-tag'>CODE</span>

{code_res}", unsafe_allow_html=True)
st.session_state.messages.append({"role": "assistant", "tag": "CODE", "content": code_res})
# 3. RESEARCH & RAG (v31)
else:
with st.spinner("🔍 İnternet Katmanları Kazınıyor..."):
# Check local memory
mem_data = next((v for k, v in brain.items() if k in p_low), None)
# Scrape academic data
report, sources = academic_engine(prompt)
final_response = ""
if mem_data:
final_response += f"💡 **Hafıza Verisi:** {mem_data}\n\n---\n"
final_response += f"### 📚 Akademik Sentez\n{report}"
st.markdown(f"<span class='agent-tag'>RESEARCH</span>

{final_response}", unsafe_allow_html=True)
if sources:
st.markdown("**🔗 Kaynaklar:**")
for s in sources: st.markdown(f"- {s}")
st.session_state.messages.append({"role": "assistant", "tag": "RESEARCH", "content": final_response})
if **name** == "**main**":
main()
```

```
