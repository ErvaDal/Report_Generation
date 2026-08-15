using System.Collections.Generic;
using System.Text.Json.Serialization;

namespace Frontend.Models
{
    // Riskleri tutacak alt sınıf
    public class RiskViewModel
    {
        [JsonPropertyName("baslik")]
        public string? Baslik { get; set; }

        [JsonPropertyName("risk_skoru")]
        public int RiskSkoru { get; set; }

        [JsonPropertyName("aciklama")]
        public string? Aciklama { get; set; }
    }

    // Ana rapor şablonu
    public class RaporViewModel
    {
        [JsonPropertyName("konu")]
        public string? Konu { get; set; }

        [JsonPropertyName("gecerlilik_suresi")]
        public string? GecerlilikSuresi { get; set; }

        [JsonPropertyName("fesih_sartlari")]
        public string? FesihSartlari { get; set; }

        [JsonPropertyName("taraflar")]
        public List<string>? Taraflar { get; set; }

        [JsonPropertyName("yonetici_ozeti")]
        public string? YoneticiOzeti { get; set; }

        [JsonPropertyName("bulunan_riskler")]
        public List<RiskViewModel>? BulunanRiskler { get; set; }
    }
}