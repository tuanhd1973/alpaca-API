using Alpaca.Api;

// Load from .env file - try multiple paths
var possiblePaths = new[] {
    Path.Combine(Directory.GetCurrentDirectory(), ".env"),
    Path.Combine(Directory.GetCurrentDirectory(), "..", ".env"),
    Path.Combine(Directory.GetCurrentDirectory(), "..", "..", ".env"),
    Path.Combine(Directory.GetCurrentDirectory(), "..", "..", "..", ".env"),
    @"C:\Users\enesh\OneDrive - MEB Okullari\Masaüstü\alpaca\csharp\.env"
};

foreach (var envPath in possiblePaths)
{
    if (File.Exists(envPath))
    {
        Console.WriteLine($"Loading .env from: {envPath}");
        foreach (var line in File.ReadAllLines(envPath))
        {
            if (string.IsNullOrWhiteSpace(line) || line.StartsWith("#")) continue;
            var parts = line.Split('=', 2);
            if (parts.Length == 2)
                Environment.SetEnvironmentVariable(parts[0].Trim(), parts[1].Trim());
        }
        break;
    }
}

var apiKey = Environment.GetEnvironmentVariable("ALPACA_API_KEY") 
    ?? throw new Exception("ALPACA_API_KEY required");
var apiSecret = Environment.GetEnvironmentVariable("ALPACA_API_SECRET") 
    ?? throw new Exception("ALPACA_API_SECRET required");

// Initialize
using var client = new AlpacaClient(new AlpacaClientOptions
{
    ApiKey = apiKey,
    ApiSecret = apiSecret,
    Paper = true
});

var trading = new TradingApi(client);
var marketData = new MarketDataApi(client);

// Account
var account = await trading.GetAccountAsync();
Console.WriteLine($"Buying Power: ${account.BuyingPowerDecimal:N2}");

// Market status
var clock = await trading.GetClockAsync();
Console.WriteLine($"Market Open: {clock.IsOpen}");

// Current price
var price = await marketData.GetCurrentPriceAsync("AAPL");
Console.WriteLine($"AAPL: ${price}");

// Positions
var positions = await trading.GetPositionsAsync();
Console.WriteLine($"Positions: {positions.Length}");

Console.WriteLine("Done!");
