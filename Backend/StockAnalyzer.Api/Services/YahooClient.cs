using System.Text.Json;
using StockAnalyzer.Api.Models;

namespace StockAnalyzer.Api.Services;

public interface IYahooClient
{
    Task<(List<StockPrice> Prices, string Currency)> GetChartDataWithCurrencyAsync(string symbol, DateTime start, DateTime end);
    Task<List<StockPrice>> GetChartDataAsync(string symbol, DateTime start, DateTime end);
}

public class YahooClient : IYahooClient
{
    private readonly HttpClient _httpClient;
    private readonly ILogger<YahooClient> _logger;

    public YahooClient(HttpClient httpClient, ILogger<YahooClient> logger)
    {
        _httpClient = httpClient;
        _httpClient.DefaultRequestHeaders.Add("User-Agent", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36");
        _logger = logger;
    }

    public async Task<(List<StockPrice> Prices, string Currency)> GetChartDataWithCurrencyAsync(string symbol, DateTime start, DateTime end)
    {
        try
        {
            long startUnix = ((DateTimeOffset)start).ToUnixTimeSeconds();
            long endUnix = ((DateTimeOffset)end).ToUnixTimeSeconds();

            var url = $"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}?period1={startUnix}&period2={endUnix}&interval=1d&events=history";
            
            var response = await _httpClient.GetStringAsync(url);
            var data = JsonSerializer.Deserialize<YahooChartRoot>(response, new JsonSerializerOptions { PropertyNameCaseInsensitive = true });

            var result = data?.Chart?.Result?.FirstOrDefault();
            if (result == null) return (new List<StockPrice>(), "USD");

            var currency = result.Meta?.Currency ?? "USD";
            var timestamps = result.Timestamp;
            var quotes = result.Indicators?.Quote?.FirstOrDefault();
            var adjClose = result.Indicators?.Adjclose?.FirstOrDefault()?.Adjclose;

            var prices = new List<StockPrice>();
            if (timestamps != null && quotes != null)
            {
                for (int i = 0; i < timestamps.Count; i++)
                {
                    if (quotes.Close[i].HasValue)
                    {
                        prices.Add(new StockPrice
                        {
                            Date = DateTimeOffset.FromUnixTimeSeconds(timestamps[i]).DateTime,
                            Open = quotes.Open[i] ?? 0,
                            High = quotes.High[i] ?? 0,
                            Low = quotes.Low[i] ?? 0,
                            Close = adjClose != null && adjClose[i].HasValue ? adjClose[i].Value : quotes.Close[i].Value
                        });
                    }
                }
            }

            return (prices, currency);
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, $"Error fetching {symbol}");
            return (new List<StockPrice>(), "USD");
        }
    }

    public async Task<List<StockPrice>> GetChartDataAsync(string symbol, DateTime start, DateTime end)
    {
        var (prices, _) = await GetChartDataWithCurrencyAsync(symbol, start, end);
        return prices;
    }
}
