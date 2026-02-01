using System.Text;
using System.Text.Json;
using StockAnalyzer.Api.Models;

namespace StockAnalyzer.Api.Services;

public interface IAiService
{
    Task<string> GetCommentaryAsync(string symbol, List<StockPrice> prices, string unit);
}

public class GeminiAiService : IAiService
{
    private readonly HttpClient _httpClient;
    private readonly IConfiguration _configuration;
    private readonly ILogger<GeminiAiService> _logger;

    public GeminiAiService(HttpClient httpClient, IConfiguration configuration, ILogger<GeminiAiService> logger)
    {
        _httpClient = httpClient;
        _configuration = configuration;
        _logger = logger;
    }

    public async Task<string> GetCommentaryAsync(string symbol, List<StockPrice> prices, string unit)
    {
        var apiKey = _configuration["GeminiApiKey"];
        if (string.IsNullOrEmpty(apiKey)) 
            return "Gemini API Key bulunamadı. Lütfen appsettings.json dosyasını kontrol edin.";

        if (prices == null || !prices.Any()) return "Analiz için veri yetersiz.";

        var lastPrice = prices.Last().Close;
        var firstPrice = prices.First().Close;
        var change = ((lastPrice - firstPrice) / firstPrice) * 100;
        
        // Gemini'ye gönderilecek veri özeti
        var prompt = $@"
        Sen profesyonel bir borsa analistisin. {symbol} hissesini analiz et.
        Veriler:
        - Birim: {unit}
        - Başlangıç Fiyatı: {firstPrice:F2}
        - Son Fiyat: {lastPrice:F2}
        - Değişim: %{change:F2}
        - Veri Aralığı: Son 30 gün.

        Lütfen bu veriye dayanarak Türkçe, kısa (maksimum 3 cümle), teknik terimler içeren ve yatırımcıya ufuk açan bir yorum yaz. 
        Yatırım tavsiyesi olmadığını belirtmeyi unutma. Markdown formatında yaz.";

        var requestBody = new
        {
            contents = new[]
            {
                new { parts = new[] { new { text = prompt } } }
            }
        };

        try
        {
            var url = $"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={apiKey}";
            var response = await _httpClient.PostAsync(url, new StringContent(JsonSerializer.Serialize(requestBody), Encoding.UTF8, "application/json"));
            
            if (!response.IsSuccessStatusCode) return "AI servisine şu an ulaşılamıyor.";

            var json = await response.Content.ReadAsStringAsync();
            using var doc = JsonDocument.Parse(json);
            var aiText = doc.RootElement
                .GetProperty("candidates")[0]
                .GetProperty("content")
                .GetProperty("parts")[0]
                .GetProperty("text")
                .GetString();

            return aiText ?? "AI yorum üretemedi.";
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Gemini API error");
            return "AI analizi sırasında teknik bir hata oluştu.";
        }
    }
}