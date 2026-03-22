import streamlit as st
import google.generativeai as genai

# --- 1. AYARLAR VE BEYİN BAĞLANTISI ---
# Buraya Google AI Studio'dan aldığın API anahtarını tırnak içine yapıştır
genai.configure(api_key="AIzaSyA-G0lgtnNtHga9_DHhLTcdn3Q2_VzcbLs")
model = genai.GenerativeModel('gemini-1.5-flash-latest')

# --- 2. EKRAN TASARIMI ---
st.set_page_config(page_title="Asistan Prime v26.0", page_icon="🦉")
st.title("🦉 Asistan Prime v26.0")
st.write("9 yaşındaki başmühendis tarafından geliştirildi.")

# Sohbet geçmişini tutmak için
if "messages" not in st.session_state:
    st.session_state.messages = []

# Eski mesajları ekranda göster
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# --- 3. SOHBET MANTIĞI ---
if prompt := st.chat_input("Bir soru sor veya bir denklem yaz..."):
    # Kullanıcı mesajını ekrana bas
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Gemini'den cevap al
    with st.chat_message("assistant"):
        try:
            response = model.generate_content(prompt)
            st.markdown(response.text)
            st.session_state.messages.append({"role": "assistant", "content": response.text})
        except Exception as e:
            st.error(f"Bir hata oluştu: {e}. Lütfen API anahtarını kontrol et!")
