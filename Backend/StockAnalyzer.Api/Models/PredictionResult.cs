namespace StockAnalyzer.Api.Models;

public class PredictionRequest
{
    public string Symbol { get; set; } = string.Empty;
    public int Days { get; set; } = 30;
    public int Lookback { get; set; } = 60;
}

public class PredictionPoint
{
    public string Date { get; set; } = string.Empty;
    public decimal PriceGold { get; set; }
    public decimal PriceUsd { get; set; }
}

public class HistoricalPoint
{
    public string Date { get; set; } = string.Empty;
    public decimal PriceGold { get; set; }
    public decimal PriceUsd { get; set; }
}

public class PredictionResult
{
    public string Symbol { get; set; } = string.Empty;
    public List<PredictionPoint> Predictions { get; set; } = new();
    public List<HistoricalPoint> Historical { get; set; } = new();
    public decimal Confidence { get; set; }
    public string Trend { get; set; } = string.Empty;
    public string ModelInfo { get; set; } = string.Empty;
    public decimal LastPriceUsd { get; set; }
    public decimal LastPriceGold { get; set; }
    public decimal PredictedChangePercent { get; set; }
}
