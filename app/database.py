import lancedb
from langchain_text_splitters import RecursiveCharacterTextSplitter
from sentence_transformers import SentenceTransformer

#metinleri anlama ve matematipe çevirme
embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
#arşiv odasının adresi
db = lancedb.connect("./data")

def sozlesmeyi_veritabanina_kaydet(metin, tablo_adi="guncel_sozlesme"):
    # chunk_size'ı 1000'den 500'e düşürüyoruz
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=500, #500 harflik küçük paragraflara bölme 
        chunk_overlap=50, #örtüşme için
        separators=["\n\n", "\n", ".", " ", ""]
    )
    parcalar = text_splitter.split_text(metin) #bölüp listeye koyma
    
    veriler = []
    for i, parca in enumerate(parcalar): #tüm parçaları sırayla alıyoruz
        #har bir parçayı yapay zekanın anlayacağı matematiksel vektörlere çevirme
        vektor = embedding_model.encode(parca).tolist()
        veriler.append({
            "id": i,
            "text": parca,
            "vector": vektor
        })

    #eski sözleşme varsa sil, yenisi için yer aç
    if tablo_adi in db.table_names():
        db.drop_table(tablo_adi)
        
    tablo = db.create_table(tablo_adi, data=veriler)
    return tablo

def sozlesmeden_ilgili_kisimlari_bul(hedef_kelimeler, limit=8, tablo_adi="guncel_sozlesme"):
    try:
        tablo = db.open_table(tablo_adi)
        # Aradığımız kelimeleri vektöre çeviriyoruz
        sorgu_vektoru = embedding_model.encode(hedef_kelimeler).tolist()
        
        # En alakalı parçaları veritabanından çekiyoruz
        sonuclar = tablo.search(sorgu_vektoru).limit(limit).to_list()
        
        baglam = ""
        for sonuc in sonuclar:
            baglam += sonuc["text"] + "\n\n---\n\n"
        return baglam
    except Exception as e:
        return "" # Tablo henüz yoksa veya hata olursa boş döner