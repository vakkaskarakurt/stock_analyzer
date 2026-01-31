using System.Net;

Console.WriteLine("Yahoo Finance JSON API Testi...");

var cookies = new CookieContainer();
var handler = new HttpClientHandler
{
    CookieContainer = cookies,
    UseCookies = true,
    AutomaticDecompression = DecompressionMethods.GZip | DecompressionMethods.Deflate,
    AllowAutoRedirect = true
};

using var client = new HttpClient(handler);
client.DefaultRequestHeaders.Add("User-Agent", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36");

try {
    // 1. Auth
    await client.GetAsync("https://fc.yahoo.com"); 
    await client.GetAsync("https://finance.yahoo.com/quote/AAPL");
    var crumbResp = await client.GetAsync("https://query1.finance.yahoo.com/v1/test/getcrumb");
    var crumb = await crumbResp.Content.ReadAsStringAsync();
    Console.WriteLine($"Crumb: {crumb}");

    // 2. JSON Chart API Dene (CSV yerine)
    long start = DateTimeOffset.Now.AddMonths(-1).ToUnixTimeSeconds();
    long end = DateTimeOffset.Now.ToUnixTimeSeconds();
    
    // Chart API genellikle Crumb istemez, ama varsa ekleyelim
    // https://query1.finance.yahoo.com/v8/finance/chart/THYAO.IS?symbol=THYAO.IS&period1=...
    
    var url = $"https://query1.finance.yahoo.com/v8/finance/chart/THYAO.IS?symbol=THYAO.IS&period1={start}&period2={end}&interval=1d";
    
    Console.WriteLine($"Fetching JSON from: {url}");
    var rData = await client.GetAsync(url);
    Console.WriteLine($"JSON Status: {rData.StatusCode}");
    
    if(rData.IsSuccessStatusCode)
    {
        var json = await rData.Content.ReadAsStringAsync();
        Console.WriteLine($"Data Length: {json.Length}");
        Console.WriteLine("JSON ÇEKİMİ BAŞARILI!");
    }

} catch(Exception ex) {
    Console.WriteLine(ex.Message);
}
