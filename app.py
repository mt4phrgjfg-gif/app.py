import streamlit as st
import google.generativeai as genai

# Sayfa ayarları
st.set_page_config(page_title="Asistan Prime v26.0", page_icon="🦉")
st.title("🦉 Asistan Prime v26.0")

# --- KASADAN ANAHTARI ÇEKME ---
if "GEMINI_KEY" not in st.secrets:
    st.error("Kritik Hata: 'GEMINI_KEY' kasada (Secrets) bulunamadı!")
    st.stop()

try:
    # Anahtarı yapılandır
    genai.configure(api_key=st.secrets["GEMINI_KEY"])
    # En sağlam model ismini seçiyoruz
    model = genai.GenerativeModel('gemini-1.5-flash')
except Exception as e:
    st.error(f"Bağlantı Kurulamadı: {e}")
    st.stop()

# --- SOHBET SİSTEMİ ---
if "messages" not in st.session_state:
    st.session_state.messages = []

# Eski mesajları göster
for m in st.session_state.messages:
    with st.chat_message(m["role"]):
        st.markdown(m["content"])

# Yeni mesaj kutusu
if prompt := st.chat_input("Bir şeyler yaz..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        try:
            # Cevap üretme
            response = model.generate_content(prompt)
            st.markdown(response.text)
            st.session_state.messages.append({"role": "assistant", "content": response.text})
        except Exception as e:
            st.error(f"API Yanıt Vermiyor: {e}")
            st.info("İpucu: API anahtarın geçersiz olabilir veya Google henüz onaylamamış olabilir.")


