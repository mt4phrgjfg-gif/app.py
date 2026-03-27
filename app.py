import streamlit as st
import google.generativeai as genai

# --- 1. TASARIM ---
st.set_page_config(page_title="Asistan Prime v26.0", page_icon="🦉")
st.title("🦉 Asistan Prime v26.0")
st.caption("Güvenli Mod: Kararlı Bağlantı Aktif")

# --- 2. BAĞLANTI ---
try:
    # Secrets'tan anahtarı alıyoruz
    api_key = st.secrets["GEMINI_KEY"]
    genai.configure(api_key=api_key)
    
    # DİKKAT: Burada 'gemini-pro' kullanıyoruz çünkü 404 hatası vermeyen en sağlam model budur.
    model = genai.GenerativeModel('gemini-pro')
except Exception as e:
    st.error(f"Anahtar hatası: {e}")
    st.stop()

# --- 3. HAFIZA ---
if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# --- 4. SOHBET ---
if prompt := st.chat_input("Bana bir soru sor..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        try:
            # En sade ve çalışan komut
            response = model.generate_content(prompt)
            st.markdown(response.text)
            st.session_state.messages.append({"role": "assistant", "content": response.text})
        except Exception as e:
            st.error("Üzgünüm, bir bağlantı sorunu oldu. Lütfen tekrar deneyin.")
