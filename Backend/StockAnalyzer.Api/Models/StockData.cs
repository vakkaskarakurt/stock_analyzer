namespace StockAnalyzer.Api.Models;

public class StockPrice
{
    public DateTime Date { get; set; }
    public decimal Price { get; set; }
}

public class AnalysisResult
{
    public string Symbol { get; set; } = string.Empty;
    public string Unit { get; set; } = string.Empty;
    public decimal ChangePercentage { get; set; }
    public List<StockPrice> Prices { get; set; } = new();
}

public class StockSummary
{
    public string Symbol { get; set; } = string.Empty;
    public decimal ChangePercentage { get; set; }
    public decimal CurrentPriceInGold { get; set; }
}

// Yahoo Finance JSON DTOs
public class YahooChartRoot { public YahooChart Chart { get; set; } }
public class YahooChart { public List<YahooChartResult> Result { get; set; } }
public class YahooChartResult { public List<long> Timestamp { get; set; } public YahooChartIndicators Indicators { get; set; } }
public class YahooChartIndicators { public List<YahooChartQuote> Quote { get; set; } }
public class YahooChartQuote { public List<decimal?> Close { get; set; } }