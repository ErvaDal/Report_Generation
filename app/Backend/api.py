from fastapi import FastAPI, UploadFile, File, HTTPException
import tempfile
import os
import email.header
from markitdown import MarkItDown

# kendi yazdığım backend servisleri
from app.Backend.database import sozlesmeyi_veritabanina_kaydet, sozlesmeden_ilgili_kisimlari_bul
from app.Backend.ai_agent import analist_ajan

# API Uygulamasını Başlatıyoruz
app = FastAPI(
    title="Sözleşme Analisti API",
    description="Sözleşmeleri RAG ve LLM ile analiz eden yerel kurumsal servis."
)

# Dışarıdan İstek Alacak uç nokta
@app.post("/api/analiz-et")
async def sozlesme_analiz_et(dosya: UploadFile = File(...)):
    
    # 1. C#'tan gelen şifreli (Türkçe karakterli) dosya adını çöz
    decoded_header = email.header.decode_header(dosya.filename)
    gercek_dosya_adi = ""
    for part, encoding in decoded_header:
        if isinstance(part, bytes):
            gercek_dosya_adi += part.decode(encoding or 'utf-8')
        else:
            gercek_dosya_adi += str(part)

    # Şifresi çözülmüş gerçek isimden dosya uzantısını al
    _, dosya_uzantisi = os.path.splitext(gercek_dosya_adi)

    # 2. Dosyayı belleğe değil, geçici bir diske alıyoruz
    with tempfile.NamedTemporaryFile(delete=False, suffix=dosya_uzantisi) as tmp_file:
        tmp_file.write(await dosya.read())
        tmp_file_path = tmp_file.name

    try:
        # MarkItDown ile Dönüşüm
        md = MarkItDown()
        result = md.convert(tmp_file_path)
        metin = result.text_content
        
        if not metin or metin.strip() == "":
            raise HTTPException(status_code=400, detail="Dosya okundu ama içinde metin bulunamadı.")

        # Vektör Veritabanı ve RAG Mimarisi İşlemleri
        sozlesmeyi_veritabanina_kaydet(metin)
        
        aranacak_kavramlar = "sözleşmenin tarafları, sözleşme konusu, fesih şartları, cezai şart, tazminat, riskli yükümlülükler"
        filtrelenmis_metin = sozlesmeden_ilgili_kisimlari_bul(aranacak_kavramlar, limit=5)

        # Llama 3.2 Ajanını Tetikleme
        prompt = f"Aşağıdaki sözleşme parçalarını analiz et ve kurumsal rapor şablonunu doldur:\n\n{filtrelenmis_metin}"
        sonuc = await analist_ajan.run(
            prompt,
            model_settings={"max_tokens": 8192}
        )
        
        # Streamlit'te ekrana yazdırdığımız veriyi, burada doğrudan Geri Döndürüyoruz
        # FastAPI, senin yazdığın 'SozlesmeRaporu' objesini otomatik olarak kusursuz bir JSON'a çevirir.
        return sonuc.output

    except Exception as e:
        # Kod çökerse 500 hatası ve detayını arayüze fırlat
        raise HTTPException(status_code=500, detail=f"Analiz sırasında sunucu hatası: {str(e)}")
        
    finally:
        # İşlem bitince veya hata verince sunucuda yer kaplamaması için geçici dosyayı sil
        if os.path.exists(tmp_file_path):
            os.remove(tmp_file_path)