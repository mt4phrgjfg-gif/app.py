import streamlit as st
import google.generativeai as genai

# --- 1. SAYFA AYARLARI VE TASARIM ---
st.set_page_config(page_title="Asistan Prime v26.0", page_icon="🦉", layout="centered")

# --- 2. API ANAHTARI VE BEYİN BAĞLANTISI ---
# ÖNEMLİ: Aşağıdaki tırnak içine kendi API anahtarını yapıştır!
api_key = "AIzaSyA-G0lgtnNtHga9_DHhLTcdn3Q2_VzcbLs" 

if not api_key or api_key == "AIzaSy...":
    st.warning("⚠️ Lütfen kodun içindeki 'api_key' bölümüne kendi API anahtarını yapıştır!")
    st.stop()

# Gemini Ayarlarını Yapılandır
try:
    genai.configure(api_key=api_key)
    # En güncel ve hızlı model: gemini-1.5-flash-latest
    model = genai.GenerativeModel('gemini-1.5-flash-latest')
except Exception as e:
    st.error(f"Bağlantı Hatası: {e}")

# --- 3. YAN MENÜ (SIDEBAR) ---
with st.sidebar:
    st.title("⚙️ Kontrol Paneli")
    st.write("v26.0 Başmühendis Sürümü")
    st.divider()
    if st.button("Sohbeti Temizle"):
        st.session_state.messages = []
        st.rerun()
    st.info("Bu asistan Python ve Google Gemini API ile güçlendirildi.")

# --- 4. ANA EKRAN VE SOHBET ---
st.title("🦉 Asistan Prime")
st.caption("9 yaşındaki Başmühendis tarafından geliştirilen AI Sistemi")

# Sohbet hafızasını oluştur (Sayfa yenilense de silinmez)
if "messages" not in st.session_state:
    st.session_state.messages = []

# Eski mesajları ekrana çiz
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Kullanıcı giriş alanı
if prompt := st.chat_input("Bana bir soru sor veya bir denklem yaz..."):
    # Kullanıcının yazdığını hafızaya ekle ve ekrana bas
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Gemini'den cevap al ve ekrana bas
    with st.chat_message("assistant"):
        try:
            # Cevap üretilirken bekletme efekti
            with st.spinner("Düşünüyorum..."):
                response = model.generate_content(prompt)
                full_response = response.text
                st.markdown(full_response)
                # Cevabı hafızaya ekle
                st.session_state.messages.append({"role": "assistant", "content": full_response})
        except Exception as e:
            st.error(f"Bir hata oluştu: {e}")
            st.info("İpucu: Eğer kırmızı hata alıyorsan API anahtarını veya internetini kontrol et!")
