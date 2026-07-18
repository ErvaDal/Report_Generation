import lancedb
from langchain_text_splitters import RecursiveCharacterTextSplitter
from sentence_transformers import SentenceTransformer

embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
db = lancedb.connect("./data")

def sozlesmeyi_veritabanina_kaydet(metin, tablo_adi="guncel_sozlesme"):
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000, 
        chunk_overlap=100,
        separators=["\n\n", "\n", ".", " ", ""]
    )
    parcalar = text_splitter.split_text(metin)
    
    veriler = []
    for i, parca in enumerate(parcalar):
        vektor = embedding_model.encode(parca).tolist()
        veriler.append({
            "id": i,
            "text": parca,
            "vector": vektor
        })
    
    if tablo_adi in db.table_names():
        db.drop_table(tablo_adi)
        
    tablo = db.create_table(tablo_adi, data=veriler)
    return tablo

def sozlesmeden_ilgili_kisimlari_bul(hedef_kelimeler, limit=8, tablo_adi="guncel_sozlesme"):
    """
    Sözleşmedeki hedeflenen kavramları LanceDB'de arar ve en alakalı parçaları (chunk) getirir.
    """
    try:
        tablo = db.open_table(tablo_adi)
        # Aradığımız kelimeleri matematiğe (vektöre) çeviriyoruz
        sorgu_vektoru = embedding_model.encode(hedef_kelimeler).tolist()
        
        # En alakalı parçaları (örneğin 8 adet) veritabanından çekiyoruz
        sonuclar = tablo.search(sorgu_vektoru).limit(limit).to_list()
        
        baglam = ""
        for sonuc in sonuclar:
            baglam += sonuc["text"] + "\n\n---\n\n"
        return baglam
    except Exception as e:
        return "" # Tablo henüz yoksa veya hata olursa boş döner