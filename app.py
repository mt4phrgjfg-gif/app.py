import streamlit as st
import google.generativeai as genai

# --- 1. SAYFA AYARLARI ---
st.set_page_config(page_title="Asistan Prime v26.0", page_icon="🦉")
st.title("🦉 Asistan Prime v26.0")

# --- 2. GÜVENLİ BAĞLANTI (GEMINI) ---
try:
    # Secrets'tan anahtarı çekiyoruz
    api_key = st.secrets["GEMINI_KEY"]
    genai.configure(api_key=api_key)
    
    # Hata veren 'v1beta' yerine en kararlı modeli seçiyoruz
    # Eğer 'gemini-1.5-flash' hata verirse 'gemini-pro' otomatik devreye girer
    model = genai.GenerativeModel('gemini-1.5-flash')
    
except Exception as e:
    st.error(f"Bağlantı ayarlarında bir sorun var: {e}")
    st.stop()

# --- 3. SOHBET GEÇMİŞİ ---
if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# --- 4. MESAJLAŞMA ---
if prompt := st.chat_input("Bana bir soru sor..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        try:
            # Mesajı oluştur ve cevabı al
            response = model.generate_content(prompt)
            st.markdown(response.text)
            st.session_state.messages.append({"role": "assistant", "content": response.text})
        except Exception as e:
            # Eğer model ismi hatası verirse alternatif modeli dene
            st.warning("Model güncelleniyor, lütfen tekrar deneyin...")
            model = genai.GenerativeModel('gemini-pro')
            response = model.generate_content(prompt)
            st.markdown(response.text)
