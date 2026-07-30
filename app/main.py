import streamlit as st
import tempfile
import os
from markitdown import MarkItDown

# Modüler mimariden kendi servislerimizi çağırıyoruz
from database import sozlesmeyi_veritabanina_kaydet, sozlesmeden_ilgili_kisimlari_bul
from ai_agent import analist_ajan

st.set_page_config(page_title="Sözleşme Analisti", layout="wide") #genişlik ayarı

st.title("Otomatik Şirket İçi Rapor ve Sözleşme Analisti")
st.write("Lütfen analiz edilmesini istediğiniz sözleşmeyi (PDF veya Word formatında) yükleyin.")

#dosya yükleme alanı
uploaded_file = st.file_uploader("Bir sözleşme dosyası seçin", type=["pdf", "docx"])

if uploaded_file is not None: #dosya yüklendiğinde hemen çalışmaya başlar
    with st.spinner("Dosya MarkItDown ile işleniyor (Tablolar ve yapılar korunuyor)..."):
        #geçici bir dosya oluşturuyor
        dosya_uzantisi = f".{uploaded_file.name.split('.')[-1]}"
        with tempfile.NamedTemporaryFile(delete=False, suffix=dosya_uzantisi) as tmp_file:
            tmp_file.write(uploaded_file.getvalue())
            tmp_file_path = tmp_file.name
        
        try:
            #pdfi metne çevir
            md = MarkItDown()
            result = md.convert(tmp_file_path)
            metin = result.text_content
        except Exception as e:
            st.error(f"Dosya okunurken hata oluştu: {e}")
            metin = ""
        finally:
            #işlem bitince dosya bilgilerini bilgisayardan sil
            os.remove(tmp_file_path)
    
    if metin:
        #metni kullanıcıya gösterme
        st.success("Dosya başarıyla Markdown formatına çevrildi!")
        with st.expander("Okunan Metnin Tamamını Gör"):
            with st.container(height=400):
                st.markdown(metin)

        #analiz başlatma butonu
        if st.button("Sözleşmeyi Analiz Et"):
            # ilerleme çubuğu
            with st.status("Sözleşme analizi başlatılıyor...", expanded=True) as status:
                try:
                    # 1. Aşama Bildirimi
                    st.write("📂 1. Aşama: Sözleşme parçalanıp LanceDB vektör veritabanına kaydediliyor...")
                    sozlesmeyi_veritabanina_kaydet(metin)
                    
                    # 2. Aşama Bildirimi
                    st.write("🔍 2. Aşama: Veritabanında kritik maddeler (risk, fesih, tazminat) aranıyor...")
                    aranacak_kavramlar = "sözleşmenin tarafları, sözleşme konusu, fesih şartları, cezai şart, tazminat, riskli yükümlülükler"
                    filtrelenmis_metin = sozlesmeden_ilgili_kisimlari_bul(aranacak_kavramlar, limit=5)

                    # 3. Aşama Bildirimi
                    st.write("🧠 3. Aşama: Llama 3.2 yapay zeka modeli raporu hazırlıyor (Bu işlem biraz sürebilir)...")
                    prompt = f"Aşağıdaki sözleşme parçalarını analiz et ve kurumsal rapor şablonunu doldur:\n\n{filtrelenmis_metin}"
                    
                    # Yapay zekayı çalıştır
                    sonuc = analist_ajan.run_sync(
                        prompt,
                        model_settings={"max_tokens": 1500}
                    )
                    rapor = sonuc.output
                    
                    # Her şey bitince kutuyu yeşile çevir ve kapat
                    status.update(label="Analiz başarıyla tamamlandı! ✅", state="complete", expanded=False)
                    
                    st.subheader("1. Sözleşmenin Temel Bilgileri")
                    st.markdown(f"**Konu:** {rapor.konu}")
                    st.markdown(f"**Geçerlilik Süresi:** {rapor.gecerlilik_suresi}")
                    st.markdown(f"**Fesih Şartları:** {rapor.fesih_sartlari}")
                    
                    st.subheader("2. Taraflar")
                    for taraf in rapor.taraflar:
                        st.markdown(f"- {taraf}")
                    
                    st.subheader("3. Yönetici Özeti")
                    st.info(rapor.yonetici_ozeti)
                    
                    st.subheader("4. Tespit Edilen Riskler")
                    if rapor.bulunan_riskler:
                        for risk in rapor.bulunan_riskler:
                            renk = "🔴" if risk.risk_skoru >= 7 else "🟠" if risk.risk_skoru >= 4 else "🟢"
                            st.write(f"{renk} **{risk.baslik}** (Skor: {risk.risk_skoru}/10)")
                            st.write(f"*{risk.aciklama}*")
                            st.divider() 
                    else:
                        st.success("Sözleşmede kritik bir risk bulunamadı.")
                        
                except Exception as e: #sistemi çökertmeden ekrana yazdırma
                    st.error(f"Analiz sırasında bir hata oluştu: {e}")