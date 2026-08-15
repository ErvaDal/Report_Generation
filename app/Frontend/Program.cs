var builder = WebApplication.CreateBuilder(args);

builder.Environment.EnvironmentName = "Development";
// MVC (Model-View-Controller) yapısını projeye dahil ediyoruz
builder.Services.AddControllersWithViews();

var app = builder.Build();

// Geliştirme ortamı dışında hata yönetimi
if (!app.Environment.IsDevelopment())
{
    app.UseExceptionHandler("/Home/Error");
    app.UseHsts();
}

app.UseHttpsRedirection();

// wwwroot klasöründeki css/js dosyalarının okunabilmesi için
app.UseStaticFiles();

app.UseRouting();

app.UseAuthorization();

// Başlangıç sayfasını senin projedeki Analiz/Index olarak ayarlıyoruz
app.MapControllerRoute(
    name: "default",
    pattern: "{controller=Analiz}/{action=Index}/{id?}");

app.Run();