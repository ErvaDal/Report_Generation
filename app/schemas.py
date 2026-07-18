from pydantic import BaseModel, Field
from typing import List

class Risk(BaseModel):
    baslik: str = Field(description="Risk içeren yasal maddenin kısa başlığı")
    aciklama: str = Field(description="Bu maddenin şirket için potansiyel tehlikesi")
    risk_skoru: int = Field(description="1 ile 10 arasında değerlendirilen tehlike puanı")

class SozlesmeRaporu(BaseModel):
    taraflar: List[str] = Field(description="Sözleşmede adı geçen tüm tarafların listesi")
    konu: str = Field(description="Sözleşmenin temel amacı")
    gecerlilik_suresi: str = Field(description="Sözleşmenin başlangıç, bitiş tarihleri veya süresi")
    fesih_sartlari: str = Field(description="Sözleşmeyi iptal etme veya feshetme koşulları")
    bulunan_riskler: List[Risk] = Field(description="Sözleşmedeki kritik risklerin listesi")
    yonetici_ozeti: str = Field(description="Tüm analizlerin toparlanmış resmi kurumsal özeti")