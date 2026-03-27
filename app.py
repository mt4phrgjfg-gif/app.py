import streamlit as st
import google.generativeai as genai

# --- 1. TASARIM VE SAYFA ---
st.set_page_config(page_title="Asistan Prime v26.0", page_icon="🦉")
st.title("🦉 Asistan Prime v26.0")
st.caption("Kuantum Bilgi Motoru (Ücretsiz Sürüm) Aktif")

# --- 2. GİZLİ KASADAN ANAHTARI AL ---
try:
    # Kasadaki 'GEMINI_KEY' etiketini okuyoruz
    api_key = st.secrets["GEMINI_KEY"]
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-1.5-flash')
except Exception as e:
    st.error("Kasada anahtar bulunamadı! Lütfen Secrets ayarlarını kontrol et.")
    st.stop()

# --- 3. SOHBET HAFIZASI ---
if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# --- 4. SORU - CEVAP ---
if prompt := st.chat_input("Bana bir soru sor veya bir denklem yaz..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        try:
            response = model.generate_content(prompt)
            st.markdown(response.text)
            st.session_state.messages.append({"role": "assistant", "content": response.text})
        except Exception as e:
            st.error(f"Bir hata oluştu: {e}")
