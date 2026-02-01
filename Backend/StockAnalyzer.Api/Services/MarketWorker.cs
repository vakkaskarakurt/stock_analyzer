using Microsoft.AspNetCore.SignalR;
using StockAnalyzer.Api.Hubs;

namespace StockAnalyzer.Api.Services;

public class MarketWorker : BackgroundService
{
    private readonly IServiceProvider _serviceProvider;
    private readonly IHubContext<MarketHub> _hubContext;
    private readonly ILogger<MarketWorker> _logger;

    public MarketWorker(IServiceProvider serviceProvider, IHubContext<MarketHub> hubContext, ILogger<MarketWorker> logger)
    {
        _serviceProvider = serviceProvider;
        _hubContext = hubContext;
        _logger = logger;
    }

    protected override async Task ExecuteAsync(CancellationToken stoppingToken)
    {
        while (!stoppingToken.IsCancellationRequested)
        {
            try
            {
                using var scope = _serviceProvider.CreateScope();
                var stockService = scope.ServiceProvider.GetRequiredService<IStockService>();
                
                // Cache'i bypass etmek için yeni veri çekiyoruz
                var update = await stockService.GetMarketSummaryAsync();
                
                await _hubContext.Clients.All.SendAsync("ReceiveMarketUpdate", update, stoppingToken);
                
                _logger.LogInformation("Market update broadcasted.");
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Error in MarketWorker");
            }

            await Task.Delay(TimeSpan.FromSeconds(15), stoppingToken);
        }
    }
}
