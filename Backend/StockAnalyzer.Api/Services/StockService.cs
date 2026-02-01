using Microsoft.Extensions.Caching.Memory;
using StockAnalyzer.Api.Models;
using System.Collections.Concurrent;

namespace StockAnalyzer.Api.Services;

public interface IStockService
{
    Task<AnalysisResult> AnalyzeStockAsync(string symbol, string unit, DateTime startDate, DateTime endDate);
    Task<List<StockSummary>> GetTopPerformersAsync();
    Task<MarketSummary> GetMarketSummaryAsync();
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

    public async Task<MarketSummary> GetMarketSummaryAsync()
    {
        const string CACHE_KEY = "MarketSummary";
        if (_cache.TryGetValue(CACHE_KEY, out MarketSummary cached)) return cached;

        var endDate = DateTime.Now;
        var startDate = endDate.AddDays(-7);

        var usdTask = _yahooClient.GetChartDataAsync("USDTRY=X", startDate, endDate);
        var goldTask = _yahooClient.GetChartDataAsync("GC=F", startDate, endDate);

        await Task.WhenAll(usdTask, goldTask);

        var usd = usdTask.Result.LastOrDefault()?.Close ?? 0;
        var usdPrev = usdTask.Result.Count > 1 ? usdTask.Result[^2].Close : usd;
        
        var gold = goldTask.Result.LastOrDefault()?.Close ?? 0;
        var goldPrev = goldTask.Result.Count > 1 ? goldTask.Result[^2].Close : gold;

        var result = new MarketSummary
        {
            UsdPrice = usd,
            UsdChange = usdPrev != 0 ? ((usd - usdPrev) / usdPrev) * 100 : 0,
            GoldPrice = gold,
            GoldChange = goldPrev != 0 ? ((gold - goldPrev) / goldPrev) * 100 : 0
        };

        _cache.Set(CACHE_KEY, result, TimeSpan.FromMinutes(5));
        return result;
    }

    public async Task<List<StockSummary>> GetTopPerformersAsync()
    {
        const string CACHE_KEY = "TopPerformers_Gold";
        if (_cache.TryGetValue(CACHE_KEY, out List<StockSummary> cachedResult)) return cachedResult;

        var stockList = _configuration.GetSection("StockSettings:PopularStocks").Get<List<string>>() 
                        ?? new List<string> { "THYAO", "GARAN" };

        var endDate = DateTime.Now;
        var startDate = endDate.AddYears(-1);
        
        var usdTask = _yahooClient.GetChartDataAsync("USDTRY=X", startDate, endDate);
        var goldTask = _yahooClient.GetChartDataAsync("GC=F", startDate, endDate);
        
        await Task.WhenAll(usdTask, goldTask);
        
        var usdData = usdTask.Result;
        var goldData = goldTask.Result;

        if (!usdData.Any() || !goldData.Any()) return new List<StockSummary>();

        var firstUsd = usdData.First().Close;
        var lastUsd = usdData.Last().Close;
        var firstGold = goldData.First().Close;
        var lastGold = goldData.Last().Close;

        var results = new ConcurrentBag<StockSummary>();
        var parallelOptions = new ParallelOptions { MaxDegreeOfParallelism = 10 };
        
        await Parallel.ForEachAsync(stockList, parallelOptions, async (symbol, token) =>
        {
            try
            {
                var formattedSymbol = $"{symbol}.IS";
                var stockData = await _yahooClient.GetChartDataAsync(formattedSymbol, startDate, endDate);
                
                if (stockData.Any())
                {
                    var firstStock = stockData.First().Close;
                    var lastStock = stockData.Last().Close;

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
            catch { /* Ignore errors */ }
        });

        var finalResult = results.OrderByDescending(x => x.ChangePercentage).Take(30).ToList();
        _cache.Set(CACHE_KEY, finalResult, TimeSpan.FromMinutes(15));
        return finalResult;
    }

    public async Task<AnalysisResult> AnalyzeStockAsync(string symbol, string unit, DateTime startDate, DateTime endDate)
    {
        var formattedSymbol = symbol.ToUpper().EndsWith(".IS") && !symbol.Contains("=") 
            ? symbol.ToUpper() 
            : (symbol.Contains("=") ? symbol.ToUpper() : $"{symbol.ToUpper()}.IS");
        
        var stockPrices = await _yahooClient.GetChartDataAsync(formattedSymbol, startDate, endDate);
        if (!stockPrices.Any()) throw new Exception("Data not found");

        var result = new AnalysisResult { Symbol = symbol.ToUpper(), Unit = unit.ToUpper(), Prices = new List<StockPrice>() };

        if (unit.ToUpper() == "TRY")
        {
            result.Prices = stockPrices;
        }
        else
        {
            // Döviz/Altın Dönüşümü
            var benchmarkSymbol = unit.ToUpper() == "USD" ? "USDTRY=X" : "GC=F";
            var benchmarkData = await _yahooClient.GetChartDataAsync(benchmarkSymbol, startDate, endDate);
            var benchmarkDict = benchmarkData.ToDictionary(x => x.Date, x => x.Close);

            // Altın ise ayrıca USD kuru da lazım (Çünkü Altın verisi ONS/USD)
            Dictionary<DateTime, decimal> usdDict = null;
            if (unit.ToUpper() == "GOLD")
            {
                var usdData = await _yahooClient.GetChartDataAsync("USDTRY=X", startDate, endDate);
                usdDict = usdData.ToDictionary(x => x.Date, x => x.Close);
            }

            foreach (var s in stockPrices)
            {
                decimal divisor = 1;
                
                if (unit.ToUpper() == "USD")
                {
                    if (benchmarkDict.TryGetValue(s.Date, out var rate) && rate > 0) divisor = rate;
                }
                else if (unit.ToUpper() == "GOLD")
                {
                    if (usdDict != null && usdDict.TryGetValue(s.Date, out var usdRate) && 
                        benchmarkDict.TryGetValue(s.Date, out var goldRate) && usdRate > 0 && goldRate > 0)
                    {
                        // Formül: (TL Fiyat / Dolar Kuru) / Ons Altın Fiyatı
                        divisor = usdRate * goldRate;
                    }
                }

                if (divisor != 1)
                {
                    result.Prices.Add(new StockPrice
                    {
                        Date = s.Date,
                        Close = s.Close / divisor,
                        Open = s.Open / divisor,
                        High = s.High / divisor,
                        Low = s.Low / divisor
                    });
                }
            }
        }

        result.Prices = result.Prices.OrderBy(x => x.Date).ToList();
        
        if (result.Prices.Any())
        {
            var first = result.Prices.First().Close;
            var last = result.Prices.Last().Close;
            result.ChangePercentage = first != 0 ? ((last - first) / first) * 100 : 0;
        }

        return result;
    }
}