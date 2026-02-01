using StockAnalyzer.Api.Models;

namespace StockAnalyzer.Api.Services;

public interface IAiService
{
    Task<string> GetCommentaryAsync(string symbol, List<StockPrice> prices);
}

public class MockAiService : IAiService
{
    public Task<string> GetCommentaryAsync(string symbol, List<StockPrice> prices)
    {
        if (prices == null || !prices.Any()) return Task.FromResult("Yorum yapmak için yeterli veri yok.");

        var last = prices.Last().Close;
        var first = prices.First().Close;
        var change = ((last - first) / first) * 100;
        var trend = change > 0 ? "Yükseliş" : "Düşüş";
        var emoji = change > 0 ? "🚀" : "🔻";

        var comments = new List<string>
        {
            $"{symbol} hissesi son dönemde %{change:F2} oranında bir {trend} sergiledi. {emoji}",
            "Teknik göstergeler şu an nötr seviyede, ancak hacim artışı dikkat çekici.",
            "Yatırımcılar için kritik destek seviyeleri test ediliyor.",
            "Piyasa genelindeki dalgalanmalardan etkileniyor gibi görünüyor.",
            "Uzun vadeli trend bozulmamış, ancak kısa vadede düzeltme gelebilir."
        };

        var random = new Random();
        var selectedComment = comments[random.Next(comments.Count)];

        return Task.FromResult($"**Yapay Zeka Analizi:**\n\n{selectedComment}\n\n*Not: Bu bir yatırım tavsiyesi değildir.*");
    }
}
