using System.Collections.Concurrent;
using Microsoft.Extensions.Caching.Memory;
using StockAnalyzer.Api.Models;

namespace StockAnalyzer.Api.Services;

public interface IStockService
{
    Task<MarketSummary> GetMarketSummaryAsync();
    Task<List<StockSummary>> GetTopPerformersAsync();
    Task<AnalysisResult> AnalyzeStockAsync(string symbol, string unit, DateTime startDate, DateTime endDate);
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
        if (_cache.TryGetValue(CACHE_KEY, out MarketSummary cachedResult)) return cachedResult;

        var usd = (await _yahooClient.GetChartDataAsync("USDTRY=X", DateTime.Now.AddDays(-5), DateTime.Now)).Last().Close;
        var usdPrev = (await _yahooClient.GetChartDataAsync("USDTRY=X", DateTime.Now.AddDays(-10), DateTime.Now.AddDays(-5))).Last().Close;
        
        var gold = (await _yahooClient.GetChartDataAsync("GC=F", DateTime.Now.AddDays(-5), DateTime.Now)).Last().Close;
        var goldPrev = (await _yahooClient.GetChartDataAsync("GC=F", DateTime.Now.AddDays(-10), DateTime.Now.AddDays(-5))).Last().Close;

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
                var formattedSymbol = symbol.Contains('.') ? symbol : $"{symbol}.IS";
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
                        var cleanSymbol = symbol.Replace(".IS", "").Replace(".is", "");
                        results.Add(new StockSummary
                        {
                            Symbol = cleanSymbol,
                            ChangePercentage = change,
                            CurrentPriceInGold = endVal
                        });
                    }
                }
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, $"Error fetching data for {symbol}");
            }
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
            var benchmarkSymbol = unit.ToUpper() == "USD" ? "USDTRY=X" : "GC=F";
            var benchmarkData = await _yahooClient.GetChartDataAsync(benchmarkSymbol, startDate, endDate);
            var benchmarkDict = benchmarkData.ToDictionary(x => x.Date, x => x.Close);

            Dictionary<DateTime, decimal> usdDict = null;
            if (unit.ToUpper() == "GOLD")
            {
                var usdData = await _yahooClient.GetChartDataAsync("USDTRY=X", startDate, endDate);
                usdDict = usdData.ToDictionary(x => x.Date, x => x.Close);
            }

            foreach (var p in stockPrices)
            {
                if (benchmarkDict.TryGetValue(p.Date, out decimal benchmarkVal) && benchmarkVal > 0)
                {
                    decimal convertedPrice;
                    if (unit.ToUpper() == "GOLD" && usdDict != null && usdDict.TryGetValue(p.Date, out decimal usdVal))
                    {
                        convertedPrice = (p.Close / usdVal) / benchmarkVal;
                    }
                    else
                    {
                        convertedPrice = p.Close / benchmarkVal;
                    }

                    result.Prices.Add(new StockPrice { Date = p.Date, Close = convertedPrice });
                }
            }
        }

        if (result.Prices.Count > 1)
        {
            var first = result.Prices.First().Close;
            var last = result.Prices.Last().Close;
            if (first > 0) result.ChangePercentage = ((last - first) / first) * 100;
        }

        return result;
    }
}
