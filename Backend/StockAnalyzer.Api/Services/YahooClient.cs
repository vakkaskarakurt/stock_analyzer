using StockAnalyzer.Api.Models;
using System.Text.Json;

namespace StockAnalyzer.Api.Services;

public interface IYahooClient
{
    Task<List<StockPrice>> GetChartDataAsync(string symbol, DateTime start, DateTime end);
}

public class YahooClient : IYahooClient
{
    private readonly HttpClient _httpClient;
    private readonly ILogger<YahooClient> _logger;

    public YahooClient(HttpClient httpClient, ILogger<YahooClient> logger)
    {
        _httpClient = httpClient;
        _logger = logger;
        _httpClient.DefaultRequestHeaders.Add("User-Agent", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36");
    }

    public async Task<List<StockPrice>> GetChartDataAsync(string symbol, DateTime start, DateTime end)
    {
        long startUnix = ((DateTimeOffset)start).ToUnixTimeSeconds();
        long endUnix = ((DateTimeOffset)end).ToUnixTimeSeconds();

        var url = $"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}?symbol={symbol}&period1={startUnix}&period2={endUnix}&interval=1d";

        try
        {
            var response = await _httpClient.GetAsync(url);
            
            if (!response.IsSuccessStatusCode)
            {
                _logger.LogWarning("Yahoo API returned {StatusCode} for {Symbol}", response.StatusCode, symbol);
                return new List<StockPrice>();
            }

            var json = await response.Content.ReadAsStringAsync();
            var chartData = JsonSerializer.Deserialize<YahooChartRoot>(json, new JsonSerializerOptions { PropertyNameCaseInsensitive = true });

            var result = new List<StockPrice>();
            
            var resultObj = chartData?.Chart?.Result?.FirstOrDefault();
            var quote = resultObj?.Indicators?.Quote?.FirstOrDefault();

            if (resultObj == null || resultObj.Timestamp == null || quote == null)
                return result;

            var timestamps = resultObj.Timestamp;
            var closes = quote.Close;
            var opens = quote.Open;
            var highs = quote.High;
            var lows = quote.Low;

            for (int i = 0; i < timestamps.Count; i++)
            {
                // Veri eksikliği kontrolü (bazen null gelebilir)
                if (closes[i].HasValue && opens[i].HasValue && highs[i].HasValue && lows[i].HasValue)
                {
                    var date = DateTimeOffset.FromUnixTimeSeconds(timestamps[i]).DateTime.Date;
                    result.Add(new StockPrice 
                    { 
                        Date = date, 
                        Close = closes[i].Value,
                        Open = opens[i].Value,
                        High = highs[i].Value,
                        Low = lows[i].Value
                    });
                }
            }

            return result;
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error fetching data for {Symbol}", symbol);
            return new List<StockPrice>();
        }
    }
}