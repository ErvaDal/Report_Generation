using Microsoft.AspNetCore.Mvc;
using Microsoft.AspNetCore.Http;
using Frontend.Models;
using System.Net.Http;
using System.Net.Http.Headers;
using System.Text.Json;
using System.Threading.Tasks;

namespace Frontend.Controllers
{
    public class AnalizController : Controller
    {
        private readonly HttpClient _httpClient;

        public AnalizController()
        {
            // Python FastAPI sunucunla haberleşecek istemciyi oluşturuyoruz.
            _httpClient = new HttpClient();
            
            // DİKKAT: FastAPI varsayılan olarak 8000 portunda çalışır. 
            // Eğer Python sunucun farklı bir porttaysa burayı güncelle.
            _httpClient.BaseAddress = new System.Uri("http://127.0.0.1:8000"); 
        }

        public IActionResult Index()
        {
            return View();
        }

        [HttpPost]
        public async Task<IActionResult> AnalizEt(IFormFile dosya)
        {
            if (dosya == null || dosya.Length == 0)
            {
                ViewBag.Hata = "Lütfen analiz için bir PDF veya Word dosyası seçin.";
                return View("Index");
            }

            try
            {
                // 1. C#'a yüklenen dosyayı Python'a göndermek üzere form formatına (Multipart) çeviriyoruz
                using var content = new MultipartFormDataContent();
                using var fileStream = dosya.OpenReadStream();
                using var fileContent = new StreamCo
                ntent(fileStream);
                
                fileContent.Headers.ContentType = MediaTypeHeaderValue.Parse(dosya.ContentType);
                
                // Buradaki "dosya" ismi, FastAPI'deki "dosya: UploadFile = File(...)" parametresiyle aynı olmak zorundadır
                content.Add(fileContent, "dosya", dosya.FileName); 

                // 2. Python API'sine POST isteğini atıyoruz
                var response = await _httpClient.PostAsync("/api/analiz-et", content);

                if (response.IsSuccessStatusCode)
                {
                    // 3. Başarılı olursa FastAPI'den gelen JSON verisini okuyoruz
                    var jsonString = await response.Content.ReadAsStringAsync();
                    
                    // JSON'ı senin yazdığın RaporViewModel class'ına dönüştürüyoruz
                    var gercekAnalizSonucu = JsonSerializer.Deserialize<RaporViewModel>(jsonString);

                    // Gerçek verilerle Sonuc sayfasını açıyoruz
                    return View("Sonuc", gercekAnalizSonucu);
                }
                else
                {
                    // Python tarafında (Örn: HTTPException) bir hata fırlatılırsa bunu yakalayıp ekrana basıyoruz
                    var errorContent = await response.Content.ReadAsStringAsync();
                    ViewBag.Hata = $"Yapay zeka servisi bir hata döndürdü. Kod: {response.StatusCode} Detay: {errorContent}";
                    return View("Index");
                }
            }
            catch (System.Exception ex)
            {
            / Sunucu kapalıysa veya ulaşılamıyorsa düşeceği yer
                ViewBag.Hata = $"Python arka uç sunucusuna bağlanılamadı. Sunucunun açık olduğundan emin olun. Hata: {ex.Message}";
                return View("Index");
            }
        }

        public IActionResult Sonuc()
        {
            return RedirectToAction("Index");
        }
    }
}




