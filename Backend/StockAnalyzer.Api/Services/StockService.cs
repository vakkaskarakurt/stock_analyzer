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

    private const string SYMBOL_USD = "USDTRY=X";
    private const string SYMBOL_GOLD = "GC=F";
    private const string SYMBOL_BIST100 = "XU100.IS";
    private const string SYMBOL_NASDAQ = "^IXIC";

    // Known non-BIST symbols to prevent auto-appending .IS
    private static readonly HashSet<string> _nonBistSymbols = new() 
    { 
        "AAPL", "MSFT", "GOOGL", "AMZN", "TSLA", "NVDA", "META", "NFLX", "AMD", "INTC", 
        "IBM", "ORCL", "PLTR", "COIN", "QCOM", "BTC-USD", "ETH-USD", "XRP-USD" 
    };

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

        var usdTask = _yahooClient.GetChartDataAsync(SYMBOL_USD, DateTime.Now.AddDays(-5), DateTime.Now);
        var goldTask = _yahooClient.GetChartDataAsync(SYMBOL_GOLD, DateTime.Now.AddDays(-5), DateTime.Now);
        var bistTask = _yahooClient.GetChartDataAsync(SYMBOL_BIST100, DateTime.Now.AddDays(-5), DateTime.Now);
        var nasdaqTask = _yahooClient.GetChartDataAsync(SYMBOL_NASDAQ, DateTime.Now.AddDays(-5), DateTime.Now);
        
        var usdPrevTask = _yahooClient.GetChartDataAsync(SYMBOL_USD, DateTime.Now.AddDays(-10), DateTime.Now.AddDays(-5));
        var goldPrevTask = _yahooClient.GetChartDataAsync(SYMBOL_GOLD, DateTime.Now.AddDays(-10), DateTime.Now.AddDays(-5));
        var bistPrevTask = _yahooClient.GetChartDataAsync(SYMBOL_BIST100, DateTime.Now.AddDays(-10), DateTime.Now.AddDays(-5));
        var nasdaqPrevTask = _yahooClient.GetChartDataAsync(SYMBOL_NASDAQ, DateTime.Now.AddDays(-10), DateTime.Now.AddDays(-5));

        await Task.WhenAll(usdTask, goldTask, bistTask, nasdaqTask, usdPrevTask, goldPrevTask, bistPrevTask, nasdaqPrevTask);

        var usdData = await usdTask;
        var goldData = await goldTask;
        var bistData = await bistTask;
        var nasdaqData = await nasdaqTask;

        var usdPrevData = await usdPrevTask;
        var goldPrevData = await goldPrevTask;
        var bistPrevData = await bistPrevTask;
        var nasdaqPrevData = await nasdaqPrevTask;

        decimal usd = usdData.Any() ? usdData.Last().Close : 0;
        decimal usdPrev = usdPrevData.Any() ? usdPrevData.Last().Close : 0;
        
        decimal gold = goldData.Any() ? goldData.Last().Close : 0;
        decimal goldPrev = goldPrevData.Any() ? goldPrevData.Last().Close : 0;

        decimal bist = bistData.Any() ? bistData.Last().Close : 0;
        decimal bistPrev = bistPrevData.Any() ? bistPrevData.Last().Close : 0;

        decimal nasdaq = nasdaqData.Any() ? nasdaqData.Last().Close : 0;
        decimal nasdaqPrev = nasdaqPrevData.Any() ? nasdaqPrevData.Last().Close : 0;

        var result = new MarketSummary
        {
            UsdPrice = usd,
            UsdChange = usdPrev != 0 ? ((usd - usdPrev) / usdPrev) * 100 : 0,
            GoldPrice = gold,
            GoldChange = goldPrev != 0 ? ((gold - goldPrev) / goldPrev) * 100 : 0,
            Bist100Price = bist,
            Bist100Change = bistPrev != 0 ? ((bist - bistPrev) / bistPrev) * 100 : 0,
            NasdaqPrice = nasdaq,
            NasdaqChange = nasdaqPrev != 0 ? ((nasdaq - nasdaqPrev) / nasdaqPrev) * 100 : 0
        };

        if (usd != 0) _cache.Set(CACHE_KEY, result, TimeSpan.FromMinutes(5));
       
        return result;
    }

    public async Task<List<StockSummary>> GetTopPerformersAsync()
    {
        const string CACHE_KEY = "TopPerformers_Gold";
        if (_cache.TryGetValue(CACHE_KEY, out List<StockSummary> cachedResult)) return cachedResult;

        var stockList = _configuration.GetSection("StockSettings:PopularStocks").Get<List<string>>() 
                        ?? new List<string> { "THYAO", "AAPL", "NVDA", "TSLA" };

        var endDate = DateTime.Now;
        var startDate = endDate.AddYears(-1);
        
        var usdTask = _yahooClient.GetChartDataAsync(SYMBOL_USD, startDate, endDate);
        var goldTask = _yahooClient.GetChartDataAsync(SYMBOL_GOLD, startDate, endDate);
        
        await Task.WhenAll(usdTask, goldTask);
        var usdData = await usdTask;
        var goldData = await goldTask;
        if (!usdData.Any() || !goldData.Any()) return new List<StockSummary>();

        var usdDict = usdData.ToDictionary(x => x.Date.Date, x => x.Close);
        var goldDict = goldData.ToDictionary(x => x.Date.Date, x => x.Close);

        var results = new ConcurrentBag<StockSummary>();
        var parallelOptions = new ParallelOptions { MaxDegreeOfParallelism = 10 };
        
        await Parallel.ForEachAsync(stockList, parallelOptions, async (symbol, token) =>
        {
            try
            {
                string formattedSymbol = symbol.ToUpper();
                if (!symbol.Contains('.') && !_nonBistSymbols.Contains(formattedSymbol) && !formattedSymbol.Contains('-'))
                {
                     formattedSymbol = $"{formattedSymbol}.IS";
                }

                var (stockPrices, baseCurrency) = await _yahooClient.GetChartDataWithCurrencyAsync(formattedSymbol, startDate, endDate);
                
                if (stockPrices.Any())
                {
                    var first = stockPrices.First();
                    var last = stockPrices.Last();

                    decimal startValInGold = 0, endValInGold = 0;

                    if (baseCurrency == "USD")
                    {
                        startValInGold = goldDict.TryGetValue(first.Date.Date, out var g1) ? first.Close / g1 : 0;
                        endValInGold = goldDict.TryGetValue(last.Date.Date, out var g2) ? last.Close / g2 : 0;
                    }
                    else
                    {
                        var u1 = usdDict.TryGetValue(first.Date.Date, out var vu1) ? vu1 : usdData.First().Close;
                        var u2 = usdDict.TryGetValue(last.Date.Date, out var vu2) ? vu2 : usdData.Last().Close;
                        var g1 = goldDict.TryGetValue(first.Date.Date, out var vg1) ? vg1 : goldData.First().Close;
                        var g2 = goldDict.TryGetValue(last.Date.Date, out var vg2) ? vg2 : goldData.Last().Close;

                        startValInGold = (first.Close / u1) / g1;
                        endValInGold = (last.Close / u2) / g2;
                    }

                    if (startValInGold > 0)
                    {
                        results.Add(new StockSummary
                        {
                            Symbol = symbol,
                            ChangePercentage = ((endValInGold - startValInGold) / startValInGold) * 100,
                            CurrentPriceInGold = endValInGold
                        });
                    }
                }
            }
            catch (Exception ex)
            {
                 _logger.LogError(ex, "Error analyzing stock {Symbol}", symbol);
            }
        });

        var finalResult = results.OrderByDescending(x => x.ChangePercentage).Take(30).ToList();
        _cache.Set(CACHE_KEY, finalResult, TimeSpan.FromMinutes(15));
        return finalResult;
    }

    public async Task<AnalysisResult> AnalyzeStockAsync(string symbol, string unit, DateTime startDate, DateTime endDate)
    {
        string upperSymbol = symbol.ToUpper();
        string formattedSymbol = upperSymbol;

        // Auto-append .IS for BIST stocks if not provided, avoiding US/Crypto symbols
        if (!upperSymbol.Contains('.') && !_nonBistSymbols.Contains(upperSymbol) && !upperSymbol.Contains('-'))
        {
            formattedSymbol = $"{upperSymbol}.IS";
        }
        
        var (stockPrices, baseCurrency) = await _yahooClient.GetChartDataWithCurrencyAsync(formattedSymbol, startDate, endDate);
        if (!stockPrices.Any()) throw new Exception("Stock not found");

        var result = new AnalysisResult { Symbol = upperSymbol, Unit = unit.ToUpper(), Prices = new List<StockPrice>() };

        var usdData = await _yahooClient.GetChartDataAsync(SYMBOL_USD, startDate, endDate);
        var usdDict = usdData.ToDictionary(x => x.Date.Date, x => x.Close);
        
        var goldData = await _yahooClient.GetChartDataAsync(SYMBOL_GOLD, startDate, endDate);
        var goldDict = goldData.ToDictionary(x => x.Date.Date, x => x.Close);

        foreach (var p in stockPrices)
        {
            decimal priceInTargetUnit = p.Close;
            var date = p.Date.Date;
            
            decimal priceInUsd = baseCurrency == "USD" ? p.Close : (usdDict.TryGetValue(date, out var uVal) ? p.Close / uVal : p.Close / usdData.Last().Close);

            if (unit == "TRY")
            {
                priceInTargetUnit = usdDict.TryGetValue(date, out var uVal2) ? priceInUsd * uVal2 : priceInUsd * usdData.Last().Close;
            }
            else if (unit == "GOLD")
            {
                priceInTargetUnit = goldDict.TryGetValue(date, out var gVal) ? priceInUsd / gVal : priceInUsd / goldData.Last().Close;
            }
            else
            {
                priceInTargetUnit = priceInUsd;
            }

            result.Prices.Add(new StockPrice { Date = p.Date, Open = p.Open, High = p.High, Low = p.Low, Close = priceInTargetUnit });
        }

        if (result.Prices.Count > 1)
        {
            var f = result.Prices.First().Close;
            var l = result.Prices.Last().Close;
            if (f > 0) result.ChangePercentage = ((l - f) / f) * 100;
        }

        return result;
    }
}
