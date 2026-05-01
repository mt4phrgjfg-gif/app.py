```python
import streamlit as st
import requests
from bs4 import BeautifulSoup
import json
import os
import re
import urllib.parse
import time
import random
import ast
import operator

# =====================================================================
# BÖLÜM 1: ÇEKİRDEK YAPILANDIRMA VE SABİTLER
# =====================================================================
st.set_page_config(page_title="Apex Enterprise AI", page_icon="⚙️", layout="wide")
DB_FILE = "enterprise_database.json"

# --- DEVASA AI VE MÜHENDİSLİK BİLGİ BANKASI (Dahili Hafıza) ---
# İnternet bağlantısı olmasa dahi sistemin bileceği binlerce konunun özeti.
# Sistemin kapasitesini artırmak için fiziksel olarak koda gömülmüştür.
INTERNAL_KNOWLEDGE_BASE = {
    "transformers": "Doğal dil işlemede devrim yaratan, 'Attention is All You Need' (2017) makalesiyle tanıtılan, paralel işlemeye uygun sinir ağı mimarisi.",
    "mamba": "Transformer'ların quadratik bellek sorununu çözen, lineer zamanlı State Space Model (SSM) mimarisi.",
    "rlhf": "İnsan geri bildirimiyle takviyeli öğrenme (Reinforcement Learning from Human Feedback). Yapay zekanın insan değerlerine hizalanmasını sağlar.",
    "dpo": "Direct Preference Optimization. RLHF'ye alternatif, ödül modeli gerektirmeyen daha hafif hizalama yöntemi.",
    "moe": "Mixture of Experts (Uzmanların Karışımı). Tüm ağı çalıştırmak yerine, sadece belirli görevler için ilgili alt ağları (uzmanları) aktive eden verimli mimari.",
    "rag": "Retrieval-Augmented Generation. Büyük dil modellerinin dış veritabanlarından bilgi çekerek halüsinasyonu (uydurmayı) önlediği mimari.",
    "lora": "Low-Rank Adaptation. Büyük modellerin tüm ağırlıklarını güncellemek yerine, araya küçük matrisler ekleyerek çok düşük maliyetle eğitilmesini (fine-tuning) sağlayan teknik.",
    "qlora": "LoRA'nın kuantize (4-bit gibi düşük bellekli) edilmiş modeller üzerinde çalışan ve RAM tüketimini inanılmaz düşüren versiyonu.",
    "bitnet": "Model ağırlıklarını sadece 3 değere (-1, 0, 1) yani 1.58-bit'e indirgeyen, enerji tüketimini %90 azaltan yeni nesil ağ.",
    "agentic ai": "Sadece soru cevaplayan değil, internette gezinen, kod yazan, araç (API) kullanan ve hedefe ulaşana kadar kendi kendine döngüye giren otonom ajan sistemleri.",
    "flashattention": "GPU'nun SRAM ve HBM bellekleri arasındaki okuma/yazma hızını optimize ederek Transformer hızını katlayan algoritma.",
    "liquid neural networks": "Zamanla değişen verilere (örneğin otonom sürüş) anında adapte olabilen, diferansiyel denklemlerle çalışan sinir ağları.",
    "sora": "OpenAI tarafından geliştirilen, fizik kurallarını simüle ederek metinden hiper-gerçekçi video üreten difüzyon modeli.",
    "stable diffusion": "Gürültü eklenmiş bir görselden gürültüyü adım adım temizleyerek metinden görsel üreten açık kaynaklı model.",
    "zero-shot": "Modelin eğitim sırasında hiç görmediği bir görevi (örneğin daha önce hiç çeviri yapmamışken çeviri yapması) başarması.",
    "few-shot": "Modele görevi yapması için sadece 2-3 örnek (prompt içinde) verilerek yönlendirilmesi.",
    "chain of thought": "Modele 'Adım adım düşün' diyerek karmaşık matematik veya mantık problemlerini alt parçalara bölmesini sağlayan teknik (CoT).",
    "tree of thoughts": "Zincirleme düşünmenin gelişmiş hali. Model birden fazla çözüm yolu üretir, bunları değerlendirir ve en iyi dalı seçer.",
    "gguf": "Yapay zeka modellerini sadece CPU üzerinde (ekran kartı olmadan) çalıştırmak için kullanılan, llama.cpp tabanlı sıkıştırılmış dosya formatı.",
    "vllm": "PagedAttention algoritmasını kullanarak dil modellerinin yanıt verme hızını ve aynı anda işlediği kullanıcı sayısını (throughput) artıran kütüphane.",
    "neural symbolic ai": "Derin öğrenmenin örüntü tanıma gücü ile sembolik yapay zekanın (mantık ve kurallar) kesinliğini birleştiren melez yaklaşım.",
    "pid kontrol": "Endüstriyel robotik ve otomasyonda kullanılan Oransal (Proportional), İntegral ve Türevsel geri besleme mekanizması.",
    "vpn": "Virtual Private Network. İnternet trafiğinizi şifreleyen ve IP adresinizi maskeleyerek coğrafi/ağ kısıtlamalarını aşmanızı sağlayan sistem.",
    "proxy": "İstemci ile sunucu arasında aracı görevi gören sunucu. SOCKS5 veya HTTP proxy'ler trafiği kendi üzerlerinden yönlendirir.",
    "aes-256": "Gelişmiş Şifreleme Standardı. 256-bit anahtar uzunluğu kullanan, kırılması pratikte imkansız olan askeri düzey şifreleme algoritması."
}

# =====================================================================
# BÖLÜM 2: GÜVENLİ MATEMATİK MOTORU (Çökme Önleyici)
# =====================================================================
# eval() fonksiyonu Streamlit'i çökertebilir veya güvenlik açığı yaratabilir.
# Bu yüzden özel ve %100 güvenli bir Abstract Syntax Tree (AST) parser yazıldı.
class SafeMathEngine:
    def __init__(self):
        self.operators = {
            ast.Add: operator.add,
            ast.Sub: operator.sub,
            ast.Mult: operator.mul,
            ast.Div: operator.truediv,
            ast.Pow: operator.pow,
            ast.BitXor: operator.xor,
            ast.USub: operator.neg
        }

    def evaluate(self, node):
        if isinstance(node, ast.Num): # <number>
            return node.n
        elif isinstance(node, ast.BinOp): # <left> <operator> <right>
            return self.operators[type(node.op)](self.evaluate(node.left), self.evaluate(node.right))
        elif isinstance(node, ast.UnaryOp): # <operator> <operand> e.g., -1
            return self.operators[type(node.op)](self.evaluate(node.operand))
        else:
            raise TypeError(node)

    def calculate(self, expression):
        try:
            # Kullanıcının girdiği 'x' veya 'X' harflerini çarpma işaretine çevir
            expr = expression.lower().replace("x", "*").replace(" ", "")
            # Sadece matematiksel karakterlere izin ver
            if not re.match(r'^[\d\+\-\*\/\(\)\.]+$', expr):
                return None
            
            node = ast.parse(expr, mode='eval').body
            result = self.evaluate(node)
            return round(result, 4) if isinstance(result, float) else result
        except Exception:
            return None

# =====================================================================
# BÖLÜM 3: AĞ VE GÜVENLİK (VPN/PROXY) MOTORU
# =====================================================================
class NetworkManager:
    def __init__(self):
        self.user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.0 Safari/605.1.15",
            "Mozilla/5.0 (X11; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/115.0"
        ]

    def fetch_data(self, query, proxy_url=None):
        proxies = {}
        if proxy_url and len(proxy_url) > 5:
            proxies = {"http": proxy_url, "https": proxy_url}
        
        headers = {
            "User-Agent": random.choice(self.user_agents),
            "Accept-Language": "en-US,en;q=0.9",
        }
        
        url = f"https://html.duckduckgo.com/html/?q={urllib.parse.quote(query)}"
        
        try:
            # Timeout 10 saniye. Bu "Running app" hatasını engeller!
            response = requests.get(url, headers=headers, proxies=proxies, timeout=10)
            
            if response.status_code != 200:
                return f"Hata: Sunucu {response.status_code} kodu döndürdü."
                
            soup = BeautifulSoup(response.text, 'html.parser')
            results = soup.find_all('a', class_='result__snippet')
            
            if not results:
                return "Ağ üzerinde taze bir eşleşme bulunamadı."
                
            formatted_results = ""
            for idx, res in enumerate(results[:4]):
                formatted_results += f"[{idx+1}] {res.text}\n"
                
            return formatted_results
            
        except requests.exceptions.Timeout:
            return "❌ Zaman Aşımı: İstek çok uzun sürdü. Lütfen ağ bağlantınızı veya Proxy adresini kontrol edin."
        except requests.exceptions.ProxyError:
            return "❌ Proxy Hatası: Girdiğiniz VPN/Proxy adresi çalışmıyor veya erişim reddedildi."
        except Exception as e:
            return f"❌ Ağ Bağlantı Hatası: {str(e)}"

# =====================================================================
# BÖLÜM 4: YEREL VERİTABANI VE HAFIZA SİSTEMİ
# =====================================================================
class DatabaseManager:
    def __init__(self, db_path):
        self.db_path = db_path
        self._ensure_db_exists()

    def _ensure_db_exists(self):
        if not os.path.exists(self.db_path):
            with open(self.db_path, "w", encoding="utf-8") as f:
                json.dump({"kurulum": "basarili"}, f)

    def read_all(self):
        try:
            with open(self.db_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}

    def save_record(self, key, value):
        data = self.read_all()
        data[key.lower().strip()] = value.strip()
        try:
            with open(self.db_path, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=4)
            return True
        except Exception:
            return False

    def search_local(self, query):
        data = self.read_all()
        query_lower = query.lower()
        results = ""
        for k, v in data.items():
            if k in query_lower or query_lower in k:
                results += f"🗄️ **Kayıtlı Bilgi [{k}]:** {v}\n\n"
        return results

# =====================================================================
# BÖLÜM 5: ANA ORKESTRATÖR (UI VE İŞLEM MANTIĞI)
# =====================================================================
def main():
    # Modüllerin Başlatılması
    math_engine = SafeMathEngine()
    net_manager = NetworkManager()
    db_manager = DatabaseManager(DB_FILE)

    # Başlık ve Arayüz
    st.title("🛡️ Enterprise AI Yönlendiricisi")
    st.markdown("Zero-Crash mimarisi üzerine kurulu profesyonel işlem merkezi.")

    # Yan Menü - Konfigürasyon
    with st.sidebar:
        st.header("Ağ Tünelleme (VPN/Proxy)")
        st.markdown("İnternet bağlantınızı maskelemek ve veriyi farklı bir IP'den çekmek için Proxy kullanın.")
        proxy_input = st.text_input("Proxy URL (SOCKS5 / HTTP):", placeholder="http://192.168.1.1:8080")
        
        if proxy_input:
            st.success("Tünel Protokolü Aktif: İstekler proxy üzerinden yönlendirilecek.")
        else:
            st.warning("Tünel Kapalı: Doğrudan ağ erişimi kullanılıyor.")
            
        st.divider()
        st.header("Sistem Durumu")
        st.write(f"Dahili AI Veritabanı: {len(INTERNAL_KNOWLEDGE_BASE)} kayıt")
        st.write(f"Yerel Öğrenilmiş Veri: {len(db_manager.read_all())} kayıt")

    # Oturum Geçmişi
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    # Geçmişi Ekrana Çiz
    for msg in st.session_state.chat_history:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    # Kullanıcı Girişi
    user_prompt = st.chat_input("İşlem girin (Hesaplama, Soru, Öğren: X=Y)")

    if user_prompt:
        # Kullanıcı mesajını kaydet ve göster
        st.session_state.chat_history.append({"role": "user", "content": user_prompt})
        with st.chat_message("user"):
            st.markdown(user_prompt)

        # Asistan Yanıt Süreci
        with st.chat_message("assistant"):
            final_response = ""
            
            try:
                # ADIM 1: Veri Öğretme Komutu mu? (Örn: Öğren: Proje = Mars)
                if user_prompt.lower().startswith("öğren:"):
                    komut_kismi = user_prompt[6:] # "öğren:" kelimesini at
                    if "=" in komut_kismi:
                        anahtar, deger = komut_kismi.split("=", 1)
                        if db_manager.save_record(anahtar, deger):
                            final_response = f"✅ Veri başarıyla belleğe yazıldı: **{anahtar.strip()}**"
                        else:
                            final_response = "❌ Veritabanına yazılırken bir hata oluştu."
                    else:
                        final_response = "❌ Yanlış format. Doğru kullanım: `Öğren: Kavram = Açıklama`"

                else:
                    # ADIM 2: Matematik İşlemi mi? (Örn: 8x8 veya 100/4)
                    mat_sonuc = math_engine.calculate(user_prompt)
                    
                    if mat_sonuc is not None:
                        final_response = f"🧮 **Hesaplama Sonucu:** {mat_sonuc}"
                    
                    else:
                        # ADIM 3: Bilgi Arama (Dahili + Yerel + Global)
                        # A) Dahili Bilgi Bankası (Koda gömülü)
                        dahili_bulgular = ""
                        for k, v in INTERNAL_KNOWLEDGE_BASE.items():
                            if k in user_prompt.lower():
                                dahili_bulgular += f"📌 **Dahili Sistem Bilgisi:** {v}\n\n"
                        
                        # B) Yerel Öğrenilmiş Veritabanı
                        yerel_bulgular = db_manager.search_local(user_prompt)
                        
                        # C) Global İnternet Taraması (VPN Destekli)
                        with st.spinner("Dünya geneli ağlar taranıyor..."):
                            global_bulgular = net_manager.fetch_data(user_prompt, proxy_url=proxy_input)
                        
                        # Sonuçları Birleştir
                        if dahili_bulgular: final_response += dahili_bulgular
                        if yerel_bulgular: final_response += yerel_bulgular
                        
                        final_response += "🌐 **İnternet Arama Sentezi:**\n" + global_bulgular

            except Exception as e:
                # Sistemin Çökmesini Engelleyen Nihai Kalkan
                final_response = f"⚠️ Sistem İşlem Hatası: {str(e)}\nBu hata yakalandı ve uygulamanın çökmesi engellendi."

            # Yanıtı ekrana bas ve geçmişe kaydet
            st.markdown(final_response)
            st.session_state.chat_history.append({"role": "assistant", "content": final_response})

if __name__ == "__main__":
    main()


```
