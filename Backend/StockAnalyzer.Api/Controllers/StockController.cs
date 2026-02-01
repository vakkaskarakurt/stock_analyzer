using Microsoft.AspNetCore.Mvc;
using StockAnalyzer.Api.Services;

namespace StockAnalyzer.Api.Controllers;

[ApiController]
[Route("api/[controller]")]
public class StockController : ControllerBase
{
    private readonly IStockService _stockService;

    public StockController(IStockService stockService)
    {
        _stockService = stockService;
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
}