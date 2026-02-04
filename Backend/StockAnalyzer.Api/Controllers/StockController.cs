using Microsoft.AspNetCore.Mvc;
using StockAnalyzer.Api.Services;

namespace StockAnalyzer.Api.Controllers;

[ApiController]
[Route("api/[controller]")]
public class StockController : ControllerBase
{
    private readonly IStockService _stockService;
    private readonly IPredictionService _predictionService;

    public StockController(IStockService stockService, IPredictionService predictionService)
    {
        _stockService = stockService;
        _predictionService = predictionService;
    }

    [HttpGet("analyze")]
    public async Task<IActionResult> Analyze(
        [FromQuery] string symbol, 
        [FromQuery] string unit = "USD", 
        [FromQuery] DateTime? start = null, 
        [FromQuery] DateTime? end = null)
    {
        var endDate = end ?? DateTime.Now;
        var startDate = start ?? endDate.AddMonths(-1);

        var result = await _stockService.AnalyzeStockAsync(symbol, unit, startDate, endDate);
        return Ok(result);
    }

    [HttpGet("top-performers")]
    public async Task<IActionResult> GetTopPerformers()
    {
        var result = await _stockService.GetTopPerformersAsync();
        return Ok(result);
    }

    [HttpGet("market-summary")]
    public async Task<IActionResult> GetMarketSummary()
    {
        var result = await _stockService.GetMarketSummaryAsync();
        return Ok(result);
    }

    [HttpGet("predict")]
    public async Task<IActionResult> Predict(
        [FromQuery] string symbol,
        [FromQuery] int days = 30,
        [FromQuery] int lookback = 60)
    {
        var result = await _predictionService.PredictAsync(symbol, days, lookback);
        return Ok(result);
    }
}