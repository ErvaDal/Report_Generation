# 📄 Yapay Zeka Destekli Hukuki Sözleşme Analiz Sistemi (RAG Tabanlı)

Bu proje, uzun ve karmaşık hukuki sözleşmeleri analiz etmek, riskli maddeleri tespit etmek ve yapılandırılmış veri (JSON) elde etmek amacıyla geliştirilmiş yapay zeka destekli bir web uygulamasıdır. 

Sistem, veri gizliliğini sağlamak amacıyla bulut tabanlı API'ler yerine tamamen yerel (on-premise) çalışan **Ollama** modellerini (Qwen 2.5) ve RAG mimarisini kullanmaktadır.

## 🚀 Öne Çıkan Özellikler

* **Yerel LLM Entegrasyonu:** Veri sızıntısını önlemek için Ollama üzerinden yerel Qwen 2.5 (3B/7B) modelleri ile çalışır.
* **RAG Mimarisi:** LanceDB vektör veritabanı kullanılarak uzun metinler parçalanır (chunking), vektörleştirilir (embedding) ve sadece en alakalı maddeler yapay zekaya bağlam olarak sunulur.
* **Katı JSON Çıktısı:** LLM halüsinasyonlarını ve sözdizimi hatalarını (Llama 3.2 kaçış karakteri hataları vb.) önlemek için API seviyesinde Regex ve Pydantic AI filtrelemesi uygulanır.
* **Güvenli Bellek Yönetimi:** Yüklenen büyük belgeler RAM'i şişirmemek adına geçici dizinlere (temp) yazılır ve analiz sonrası `finally` bloklarıyla otomatik olarak temizlenir.
* **Modern Web Arayüzü:** REST API üzerine inşa edilmiş, asenkron iletişim kuran kullanıcı dostu web arayüzü (Kullanım kolaylığı için C# masaüstü mimarisinden web mimarisine taşınmıştır).

## 🛠️ Kullanılan Teknolojiler

* **Backend:** Python 3.x, FastAPI, Uvicorn
* **AI & NLP:** Ollama, Pydantic AI, Qwen 2.5 (3B)
* **Vektör Veritabanı:** LanceDB
* **Frontend:** HTML5, CSS3, JavaScript (Fetch API)
* **Veri Doğrulama:** Pydantic

## ⚙️ Kurulum Adımları

Projeyi yerel ortamınızda çalıştırmak için aşağıdaki adımları sırasıyla izleyin:

### 1. Depoyu Klonlayın

### 2. Sanal Ortam Oluşturun
  python -m venv venv
  Windows için:
  venv\Scripts\activate
  Linux/Mac için:
  source venv/bin/activate

### 3. Bağımlılıkları yükleyin
  pip install -r requirements.txt

### 4. Ollama ve Yapay Zeka Modelini Hazırlayın
  ollama pull qwen2.5:3b (başka bir model de yükleyebilirsiniz)

Tüm kurulumlar tamamlandıktan sonra FastAPI sunucusunu ayağa kaldırmak için aşağıdaki komutu çalıştırın: 
uvicorn app.Backend.api:app --reload

