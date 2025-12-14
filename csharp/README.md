# Alpaca API Client - C# (.NET)

.NET client for Alpaca Trading and Market Data APIs.

## Requirements

- .NET 8.0+

## Build

```bash
dotnet build
```

## Quick Start

```csharp
using Alpaca.Api;

var client = new AlpacaClient(new AlpacaClientOptions
{
    ApiKey = Environment.GetEnvironmentVariable("ALPACA_API_KEY")!,
    ApiSecret = Environment.GetEnvironmentVariable("ALPACA_API_SECRET")!,
    Paper = true
});

var trading = new TradingApi(client);
var marketData = new MarketDataApi(client);

// Account
var account = await trading.GetAccountAsync();
Console.WriteLine($"Buying Power: ${account.BuyingPower:N2}");

// Order
var order = await trading.BuyAsync("AAPL", 10);

// Market Data
var price = await marketData.GetCurrentPriceAsync("AAPL");
Console.WriteLine($"AAPL: ${price}");
```

## Run Example

```bash
cd Examples
dotnet run
```
