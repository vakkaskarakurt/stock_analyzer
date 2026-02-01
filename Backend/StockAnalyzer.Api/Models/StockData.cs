namespace StockAnalyzer.Api.Models;

public class StockPrice
{
    public DateTime Date { get; set; }
    public decimal Open { get; set; }
    public decimal High { get; set; }
    public decimal Low { get; set; }
    public decimal Close { get; set; }
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

public class MarketSummary
{
    public decimal UsdPrice { get; set; }
    public decimal UsdChange { get; set; }
    public decimal GoldPrice { get; set; } // ONS
    public decimal GoldChange { get; set; }
}

// Yahoo Finance JSON DTOs
public class YahooChartRoot { public YahooChart Chart { get; set; } }
public class YahooChart { public List<YahooChartResult> Result { get; set; } }
public class YahooChartResult { public List<long> Timestamp { get; set; } public YahooChartIndicators Indicators { get; set; } }
public class YahooChartIndicators { public List<YahooChartQuote> Quote { get; set; } }
public class YahooChartQuote 
{ 
    public List<decimal?> Open { get; set; }
    public List<decimal?> High { get; set; }
    public List<decimal?> Low { get; set; }
    public List<decimal?> Close { get; set; } 
}
