using Microsoft.Extensions.Caching.Memory;
using StockAnalyzer.Api.Models;
using System.Collections.Concurrent;

namespace StockAnalyzer.Api.Services;

public interface IStockService
{
    Task<AnalysisResult> AnalyzeStockAsync(string symbol, string unit, DateTime startDate, DateTime endDate);
    Task<List<StockSummary>> GetTopPerformersAsync();
}

public class StockService : IStockService
{
    private readonly IYahooClient _yahooClient;
    private readonly IMemoryCache _cache;
    private readonly IConfiguration _configuration;
    private readonly ILogger<StockService> _logger;

    public StockService(IYahooClient yahooClient, IMemoryCache cache, IConfiguration configuration, ILogger<StockService> logger)
    {
        _yahooClient = yahooClient;
        _cache = cache;
        _configuration = configuration;
        _logger = logger;
    }

    public async Task<List<StockSummary>> GetTopPerformersAsync()
    {
        const string CACHE_KEY = "TopPerformers_Gold";
        
        // Cache Kontrolü
        if (_cache.TryGetValue(CACHE_KEY, out List<StockSummary> cachedResult))
        {
            _logger.LogInformation("Returning cached Top Performers data.");
            return cachedResult;
        }

        _logger.LogInformation("Cache miss. Fetching fresh data for Top Performers.");

        var stockList = _configuration.GetSection("StockSettings:PopularStocks").Get<List<string>>() 
                        ?? new List<string> { "THYAO", "GARAN" }; // Fallback

        var endDate = DateTime.Now;
        var startDate = endDate.AddYears(-1);
        
        // 1. Referans Verileri
        var usdTask = _yahooClient.GetChartDataAsync("USDTRY=X", startDate, endDate);
        var goldTask = _yahooClient.GetChartDataAsync("GC=F", startDate, endDate);
        
        await Task.WhenAll(usdTask, goldTask);
        
        var usdData = usdTask.Result;
        var goldData = goldTask.Result;

        if (!usdData.Any() || !goldData.Any())
            throw new Exception("Market benchmark data (USD/Gold) unavailable.");

        var firstUsd = usdData.First().Price;
        var lastUsd = usdData.Last().Price;
        var firstGold = goldData.First().Price;
        var lastGold = goldData.Last().Price;

        var results = new ConcurrentBag<StockSummary>();

        // 2. Hisseleri Paralel Çek
        var parallelOptions = new ParallelOptions { MaxDegreeOfParallelism = 10 };
        await Parallel.ForEachAsync(stockList, parallelOptions, async (symbol, token) =>
        {
            try
            {
                var formattedSymbol = $"{symbol}.IS";
                var stockData = await _yahooClient.GetChartDataAsync(formattedSymbol, startDate, endDate);
                
                if (stockData.Any())
                {
                    var firstStock = stockData.First().Price;
                    var lastStock = stockData.Last().Price;

                    // Altın Bazlı Değişim Hesaplama
                    // 1 Yıl Önceki Altın Değeri = (HisseFiyatı / DolarKuru) / OnsAltın
                    var startVal = (firstStock / firstUsd) / firstGold;
                    var endVal = (lastStock / lastUsd) / lastGold;
                    
                    if (startVal > 0)
                    {
                        var change = ((endVal - startVal) / startVal) * 100;
                        results.Add(new StockSummary
                        {
                            Symbol = symbol,
                            ChangePercentage = change,
                            CurrentPriceInGold = endVal
                        });
                    }
                }
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Failed to process {Symbol}", symbol);
            }
        });

        var finalResult = results.OrderByDescending(x => x.ChangePercentage).Take(30).ToList();

        // Cache'e Yaz
        var cacheDuration = _configuration.GetValue<int>("StockSettings:CacheDurationMinutes", 15);
        _cache.Set(CACHE_KEY, finalResult, TimeSpan.FromMinutes(cacheDuration));

        return finalResult;
    }

    public async Task<AnalysisResult> AnalyzeStockAsync(string symbol, string unit, DateTime startDate, DateTime endDate)
    {
        // Basit Input Validasyonu
        if (string.IsNullOrWhiteSpace(symbol) || symbol.Length > 10 || !symbol.All(c => char.IsLetterOrDigit(c) || c == '.' || c == '='))
            throw new ArgumentException("Invalid stock symbol.");

        var formattedSymbol = symbol.ToUpper().EndsWith(".IS") && !symbol.Contains("=") 
            ? symbol.ToUpper() 
            : (symbol.Contains("=") ? symbol.ToUpper() : $"{symbol.ToUpper()}.IS");
        
        var stockPrices = await _yahooClient.GetChartDataAsync(formattedSymbol, startDate, endDate);
        
        if (!stockPrices.Any())
            throw new Exception($"Stock data not found for {formattedSymbol}!");

        var usdPrices = await _yahooClient.GetChartDataAsync("USDTRY=X", startDate, endDate);
        var usdDict = usdPrices.ToDictionary(x => x.Date, x => x.Price);

        var result = new AnalysisResult
        {
            Symbol = symbol.ToUpper(),
            Unit = unit.ToUpper(),
            Prices = new List<StockPrice>()
        };

        // Para birimi dönüşüm mantığı
        if (unit.ToUpper() == "USD")
        {
            foreach (var stock in stockPrices)
            {
                if (usdDict.TryGetValue(stock.Date, out var usdRate) && usdRate > 0)
                {
                    result.Prices.Add(new StockPrice { Date = stock.Date, Price = stock.Price / usdRate });
                }
            }
        }
        else if (unit.ToUpper() == "GOLD")
        {
            var goldPrices = await _yahooClient.GetChartDataAsync("GC=F", startDate, endDate);
            var goldDict = goldPrices.ToDictionary(x => x.Date, x => x.Price);

            foreach (var stock in stockPrices)
            {
                if (usdDict.TryGetValue(stock.Date, out var usdRate) && 
                    goldDict.TryGetValue(stock.Date, out var goldPrice) && 
                    usdRate > 0 && goldPrice > 0)
                {
                    var stockInUsd = stock.Price / usdRate;
                    result.Prices.Add(new StockPrice { Date = stock.Date, Price = stockInUsd / goldPrice });
                }
            }
        }
        else // TRY
        {
            result.Prices = stockPrices;
        }

        if (!result.Prices.Any())
            throw new Exception("Currency data mismatch. Try a wider date range.");

        result.Prices = result.Prices.OrderBy(x => x.Date).ToList();
        
        var first = result.Prices.First().Price;
        var last = result.Prices.Last().Price;
        result.ChangePercentage = first != 0 ? ((last - first) / first) * 100 : 0;

        return result;
    }
}
