import streamlit as st
import google.generativeai as genai

# --- 1. AYARLAR ---
st.set_page_config(page_title="Asistan Prime v26.0", page_icon="🦉")
st.title("🦉 Asistan Prime v26.0")

# --- 2. GÜVENLİ BAĞLANTI ---
try:
    # Secrets'tan anahtarı al
    api_key = st.secrets["GEMINI_KEY"]
    genai.configure(api_key=api_key)
    
    # DİKKAT: 'models/' ekini sildik, sadece model ismini yazdık
    # Bu sayede 'v1beta' hatasından kurtuluyoruz
    model = genai.GenerativeModel('gemini-1.5-flash')
    
except Exception as e:
    st.error(f"Bağlantı Ayarı Hatası: {e}")
    st.stop()

# --- 3. SOHBET ---
if "messages" not in st.session_state:
    st.session_state.messages = []

for m in st.session_state.messages:
    st.chat_message(m["role"]).write(m["content"])

if prompt := st.chat_input():
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.chat_message("user").write(prompt)
    
    try:
        # Yanıt alma
        response = model.generate_content(prompt)
        st.session_state.messages.append({"role": "assistant", "content": response.text})
        st.chat_message("assistant").write(response.text)
    except Exception as e:
        # Hata detayını temiz göster
        st.error(f"API Yanıt Vermiyor: {e}")
