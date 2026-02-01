using Moq;
using Microsoft.Extensions.Caching.Memory;
using Microsoft.Extensions.Configuration;
using Microsoft.Extensions.Logging;
using StockAnalyzer.Api.Models;
using StockAnalyzer.Api.Services;

namespace StockAnalyzer.Tests;

public class StockServiceTests
{
    private readonly Mock<IYahooClient> _mockYahooClient;
    private readonly Mock<IMemoryCache> _mockCache;
    private readonly IConfiguration _config; // Mock yerine gerçek ama in-memory config
    private readonly Mock<ILogger<StockService>> _mockLogger;
    private readonly StockService _stockService;

    public StockServiceTests()
    {
        _mockYahooClient = new Mock<IYahooClient>();
        _mockCache = new Mock<IMemoryCache>();
        _mockLogger = new Mock<ILogger<StockService>>();

        // In-Memory Configuration
        var myConfiguration = new Dictionary<string, string>
        {
            {"StockSettings:CacheDurationMinutes", "15"},
            {"StockSettings:PopularStocks:0", "THYAO"} // Array elemanı tanımlama yöntemi
        };

        _config = new ConfigurationBuilder()
            .AddInMemoryCollection(myConfiguration)
            .Build();

        // Cache Mock Setup
        var mockCacheEntry = new Mock<ICacheEntry>();
        _mockCache.Setup(m => m.CreateEntry(It.IsAny<object>())).Returns(mockCacheEntry.Object);

        _stockService = new StockService(_mockYahooClient.Object, _mockCache.Object, _config, _mockLogger.Object);
    }

    [Fact]
    public async Task GetTopPerformers_ShouldCalculateCorrectly_WhenDataExists()
    {
        // ARRANGE
        var startDate = It.IsAny<DateTime>();
        var endDate = It.IsAny<DateTime>();

        // Mock USD Data (Start: 10, End: 20 -> %100 Artış, 2x)
        var usdData = new List<StockPrice> 
        { 
            new() { Date = DateTime.Now.AddYears(-1), Close = 10 },
            new() { Date = DateTime.Now, Close = 20 }
        };

        // Mock Gold Data (Start: 1000, End: 2000 -> %100 Artış, 2x)
        var goldData = new List<StockPrice> 
        { 
            new() { Date = DateTime.Now.AddYears(-1), Close = 1000 },
            new() { Date = DateTime.Now, Close = 2000 }
        };

        // Mock Stock (THYAO)
        // Start: 100 TL
        // End: 800 TL
        // Start Altın Değeri: (100 / 10) / 1000 = 0.01 ons
        // End Altın Değeri:   (800 / 20) / 2000 = 0.02 ons
        // Değişim: (0.02 - 0.01) / 0.01 = %100 Artış
        var stockData = new List<StockPrice> 
        { 
            new() { Date = DateTime.Now.AddYears(-1), Close = 100 },
            new() { Date = DateTime.Now, Close = 800 }
        };

        _mockYahooClient.Setup(x => x.GetChartDataAsync("USDTRY=X", It.IsAny<DateTime>(), It.IsAny<DateTime>())).ReturnsAsync(usdData);
        _mockYahooClient.Setup(x => x.GetChartDataAsync("GC=F", It.IsAny<DateTime>(), It.IsAny<DateTime>())).ReturnsAsync(goldData);
        // Match any stock symbol containing THYAO
        _mockYahooClient.Setup(x => x.GetChartDataAsync(It.Is<string>(s => s.Contains("THYAO")), It.IsAny<DateTime>(), It.IsAny<DateTime>())).ReturnsAsync(stockData);

        // ACT
        var result = await _stockService.GetTopPerformersAsync();

        // ASSERT
        Assert.NotNull(result);
        var thyao = result.FirstOrDefault(x => x.Symbol == "THYAO");
        Assert.NotNull(thyao);
        
        // Hassasiyet (Precision) payı ile kontrol et
        Assert.Equal(100, thyao.ChangePercentage, 1); 
    }
}