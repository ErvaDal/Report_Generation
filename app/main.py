import streamlit as st
import tempfile
import os
from markitdown import MarkItDown
from database import sozlesmeyi_veritabanina_kaydet, sozlesmeden_ilgili_kisimlari_bul

# Modüler mimariden kendi servislerimizi çağırıyoruz
from database import sozlesmeyi_veritabanina_kaydet
from ai_agent import analist_ajan

st.set_page_config(page_title="Sözleşme Analisti", layout="wide")

st.title("📄 Otomatik Şirket İçi Rapor ve Sözleşme Analisti")
st.write("Lütfen analiz edilmesini istediğiniz sözleşmeyi (PDF veya Word formatında) yükleyin.")

uploaded_file = st.file_uploader("Bir sözleşme dosyası seçin", type=["pdf", "docx"])

if uploaded_file is not None:
    with st.spinner("Dosya MarkItDown ile işleniyor (Tablolar ve yapılar korunuyor)..."):
        dosya_uzantisi = f".{uploaded_file.name.split('.')[-1]}"
        with tempfile.NamedTemporaryFile(delete=False, suffix=dosya_uzantisi) as tmp_file:
            tmp_file.write(uploaded_file.getvalue())
            tmp_file_path = tmp_file.name
        
        try:
            md = MarkItDown()
            result = md.convert(tmp_file_path)
            metin = result.text_content
        except Exception as e:
            st.error(f"Dosya okunurken hata oluştu: {e}")
            metin = ""
        finally:
            os.remove(tmp_file_path)
    
    if metin:
        st.success("Dosya başarıyla Markdown formatına çevrildi!")
        
        with st.expander("Okunan Metnin Tamamını Gör"):
            with st.container(height=400):
                st.markdown(metin)

        if st.button("Sözleşmeyi Analiz Et"):
            with st.spinner("RAG mimarisiyle sözleşmenin kritik kısımları filtreleniyor ve analiz ediliyor..."):
                try:
                    # 1. Metni LanceDB'ye kaydet 
                    sozlesmeyi_veritabanina_kaydet(metin)
                    st.toast("Sözleşme vektör veritabanına kaydedildi! ✅")
                    
                    # 2. RAG FİLTRELEMESİ: Sadece kritik konuları ara ve getir
                    aranacak_kavramlar = "sözleşmenin tarafları, sözleşme konusu, fesih şartları, cezai şart, tazminat, riskli yükümlülükler"
                    filtrelenmis_metin = sozlesmeden_ilgili_kisimlari_bul(aranacak_kavramlar, limit=4)                    
                    # 3. Pydantic Ajanını filtrelenmiş, kısa ve öz metinle çalıştır
                    prompt = f"Aşağıdaki sözleşme parçalarını analiz et ve kurumsal rapor şablonunu doldur:\n\n{filtrelenmis_metin}"
                    # Modelin cevap verebilmesi için kelime sınırını 4000'e çıkarıyoruz
                    sonuc = analist_ajan.run_sync(
                        prompt,
                        model_settings={"max_tokens": 4000})
                    rapor = sonuc.output 
                    
                    # Sonuçları Gösterme
                    st.success("Analiz başarıyla tamamlandı!")
                    
                    st.subheader("📌 1. Sözleşmenin Temel Bilgileri")
                    st.markdown(f"**Konu:** {rapor.konu}")
                    st.markdown(f"**Geçerlilik Süresi:** {rapor.gecerlilik_suresi}")
                    st.markdown(f"**Fesih Şartları:** {rapor.fesih_sartlari}")
                    
                    st.subheader("🤝 2. Taraflar")
                    for taraf in rapor.taraflar:
                        st.markdown(f"- {taraf}")
                    
                    st.subheader("📝 3. Yönetici Özeti")
                    st.info(rapor.yonetici_ozeti)
                    
                    st.subheader("⚠️ 4. Tespit Edilen Riskler")
                    if rapor.bulunan_riskler:
                        for risk in rapor.bulunan_riskler:
                            renk = "🔴" if risk.risk_skoru >= 7 else "🟠" if risk.risk_skoru >= 4 else "🟢"
                            st.write(f"{renk} **{risk.baslik}** (Skor: {risk.risk_skoru}/10)")
                            st.write(f"*{risk.aciklama}*")
                            st.divider() 
                    else:
                        st.success("Sözleşmede kritik bir risk bulunamadı.")
                        
                except Exception as e:
                    st.error(f"Analiz sırasında bir hata oluştu: {e}")