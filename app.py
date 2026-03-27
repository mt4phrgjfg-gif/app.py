import streamlit as st
import anthropic

# --- 1. SAYFA AYARLARI ---
st.set_page_config(page_title="Asistan Prime v26.0", page_icon="🦉", layout="centered")

# --- 2. API ANAHTARI ---
# Artık anahtarı buraya yazmıyoruz, Streamlit'in kasasından çağırıyoruz.
client = anthropic.Anthropic(api_key=st.secrets["CLAUDE_KEY"])


# --- 3. YAN MENÜ ---
with st.sidebar:
    st.title("⚙️ Kontrol Paneli")
    st.write("v26.0 Başmühendis Sürümü")
    st.divider()
    if st.button("Sohbeti Temizle"):
        st.session_state.messages = []
        st.rerun()
    st.info("Bu asistan Python ve Anthropic Claude API ile güçlendirildi.")

# --- 4. ANA EKRAN ---
st.title("🦉 Asistan Prime")
st.caption("9 yaşındaki Başmühendis tarafından geliştirilen AI Sistemi")

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("Bana bir soru sor veya bir denklem yaz..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        try:
            with st.spinner("Düşünüyorum..."):
                response = client.messages.create(
                    model="claude-haiku-4-5-20251001",
                    max_tokens=1000,
                    messages=st.session_state.messages
                )
                full_response = response.content[0].text
                st.markdown(full_response)
                st.session_state.messages.append({"role": "assistant", "content": full_response})
        except Exception as e:
            st.error(f"Bir hata oluştu: {e}")
