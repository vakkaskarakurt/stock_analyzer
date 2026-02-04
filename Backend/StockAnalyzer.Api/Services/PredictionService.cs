using System.Text;
using System.Text.Json;
using StockAnalyzer.Api.Models;

namespace StockAnalyzer.Api.Services;

public interface IPredictionService
{
    Task<PredictionResult> PredictAsync(string symbol, int days = 30, int lookback = 60);
}

public class PredictionService : IPredictionService
{
    private readonly HttpClient _httpClient;
    private readonly IConfiguration _configuration;
    private readonly ILogger<PredictionService> _logger;

    private static readonly JsonSerializerOptions JsonOptions = new()
    {
        PropertyNamingPolicy = JsonNamingPolicy.SnakeCaseLower,
        PropertyNameCaseInsensitive = true
    };

    public PredictionService(
        HttpClient httpClient,
        IConfiguration configuration,
        ILogger<PredictionService> logger)
    {
        _httpClient = httpClient;
        _configuration = configuration;
        _logger = logger;

        // Configure base address from settings
        var baseUrl = _configuration["PredictionService:BaseUrl"] ?? "http://localhost:8000";
        _httpClient.BaseAddress = new Uri(baseUrl);
        _httpClient.Timeout = TimeSpan.FromMinutes(2); // Model training can take time
    }

    public async Task<PredictionResult> PredictAsync(string symbol, int days = 30, int lookback = 60)
    {
        try
        {
            var request = new PredictionRequest
            {
                Symbol = symbol.ToUpper(),
                Days = days,
                Lookback = lookback
            };

            var jsonContent = JsonSerializer.Serialize(request, JsonOptions);
            var content = new StringContent(jsonContent, Encoding.UTF8, "application/json");

            _logger.LogInformation("Requesting prediction for {Symbol} ({Days} days)", symbol, days);

            var response = await _httpClient.PostAsync("/predict", content);

            if (!response.IsSuccessStatusCode)
            {
                var errorContent = await response.Content.ReadAsStringAsync();
                _logger.LogError("Prediction service error: {StatusCode} - {Content}",
                    response.StatusCode, errorContent);
                throw new Exception($"Prediction service returned {response.StatusCode}: {errorContent}");
            }

            var responseContent = await response.Content.ReadAsStringAsync();
            var result = JsonSerializer.Deserialize<PredictionResult>(responseContent, JsonOptions);

            if (result == null)
            {
                throw new Exception("Failed to deserialize prediction response");
            }

            _logger.LogInformation("Prediction completed for {Symbol}: {Trend} ({Change}%)",
                symbol, result.Trend, result.PredictedChangePercent);

            return result;
        }
        catch (HttpRequestException ex)
        {
            _logger.LogError(ex, "Failed to connect to prediction service");
            throw new Exception("Prediction service is unavailable. Please ensure the Python service is running.", ex);
        }
        catch (TaskCanceledException ex)
        {
            _logger.LogError(ex, "Prediction request timed out");
            throw new Exception("Prediction request timed out. The model may be training.", ex);
        }
    }
}
