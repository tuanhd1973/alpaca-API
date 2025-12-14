using Alpaca.Api;

// Load from environment
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
Console.WriteLine($"Buying Power: ${account.BuyingPower:N2}");

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
