using Microsoft.AspNetCore.Mvc;
using StockAnalyzer.Api.Services;

namespace StockAnalyzer.Api.Controllers;

[ApiController]
[Route("api/[controller]")]
public class StockController : ControllerBase
{
    private readonly IStockService _stockService;
    private readonly IAiService _aiService;

    public StockController(IStockService stockService, IAiService aiService)
    {
        _stockService = stockService;
        _aiService = aiService;
    }

    [HttpGet("analyze")]
    public async Task<IActionResult> Analyze(
        [FromQuery] string symbol, 
        [FromQuery] string unit = "USD", 
        [FromQuery] DateTime? start = null, 
        [FromQuery] DateTime? end = null)
    {
        try
        {
            var endDate = end ?? DateTime.Now;
            var startDate = start ?? endDate.AddMonths(-1);

            var result = await _stockService.AnalyzeStockAsync(symbol, unit, startDate, endDate);
            return Ok(result);
        }
        catch (Exception ex)
        {
            return BadRequest(new { message = ex.Message });
        }
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

    [HttpGet("ai-comment")]
    public async Task<IActionResult> GetAiComment([FromQuery] string symbol)
    {
        // Gerçek senaryoda veriyi veritabanından veya cache'den alırız.
        // Şimdilik hızlıca son veriyi çekiyoruz.
        try 
        {
            var data = await _stockService.AnalyzeStockAsync(symbol, "TRY", DateTime.Now.AddMonths(-1), DateTime.Now);
            var comment = await _aiService.GetCommentaryAsync(symbol, data.Prices);
            return Ok(new { comment });
        }
        catch (Exception ex)
        {
            return BadRequest(new { message = ex.Message });
        }
    }
}