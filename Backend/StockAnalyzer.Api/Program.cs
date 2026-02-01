using StockAnalyzer.Api.Middleware;
using StockAnalyzer.Api.Services;

var builder = WebApplication.CreateBuilder(args);

// 1. Add Services
builder.Services.AddControllers();

// 2. Caching
// 1. Add SignalR
builder.Services.AddSignalR();
builder.Services.AddMemoryCache();

// 3. HttpClient Factory
builder.Services.AddHttpClient<IYahooClient, YahooClient>()
    .SetHandlerLifetime(TimeSpan.FromMinutes(5));

// 4. Domain Services
builder.Services.AddHttpClient();
builder.Services.AddScoped<IStockService, StockService>();
builder.Services.AddScoped<IAiService, GeminiAiService>();
builder.Services.AddHostedService<MarketWorker>();

// 5. CORS
builder.Services.AddCors(options =>
{
    options.AddPolicy("AllowAngular", policy =>
    {
        policy.WithOrigins("http://localhost:4200", "http://localhost:5035", "https://localhost:7080")
              .AllowAnyHeader()
              .AllowAnyMethod();
    });
});

var app = builder.Build();

app.UseMiddleware<ExceptionHandlingMiddleware>();
app.UseCors("AllowAngular");

app.MapHub<StockAnalyzer.Api.Hubs.MarketHub>("/marketHub");
app.MapControllers();

app.Run();