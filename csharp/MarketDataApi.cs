using System.Text.Json;

namespace Alpaca.Api;

public class MarketDataApi
{
    private readonly AlpacaClient _client;

    public MarketDataApi(AlpacaClient client) => _client = client;

    // Stock Bars
    public async Task<Dictionary<string, Bar[]>> GetStockBarsAsync(string[] symbols, string timeframe = "1Day", int limit = 100)
    {
        var endpoint = $"/v2/stocks/bars?symbols={string.Join(",", symbols)}&timeframe={timeframe}&limit={limit}";
        var response = await _client.GetAsync<JsonElement>(endpoint, AlpacaClient.MarketData);
        
        var bars = new Dictionary<string, Bar[]>();
        if (response.TryGetProperty("bars", out var barsElement))
        {
            foreach (var prop in barsElement.EnumerateObject())
            {
                bars[prop.Name] = JsonSerializer.Deserialize<Bar[]>(prop.Value.GetRawText()) ?? [];
            }
        }
        return bars;
    }

    // Stock Snapshot
    public async Task<JsonElement> GetStockSnapshotAsync(string symbol)
    {
        var endpoint = $"/v2/stocks/{symbol.ToUpper()}/snapshot";
        return await _client.GetAsync<JsonElement>(endpoint, AlpacaClient.MarketData);
    }

    // Current Price
    public async Task<decimal> GetCurrentPriceAsync(string symbol)
    {
        var snapshot = await GetStockSnapshotAsync(symbol);
        if (snapshot.TryGetProperty("latestTrade", out var trade) && trade.TryGetProperty("p", out var price))
        {
            return price.GetDecimal();
        }
        throw new Exception($"No trade data for {symbol}");
    }

    // Crypto Bars
    public async Task<Dictionary<string, Bar[]>> GetCryptoBarsAsync(string[] symbols, string timeframe = "1Day", int limit = 100)
    {
        var endpoint = $"/v1beta3/crypto/us/bars?symbols={string.Join(",", symbols)}&timeframe={timeframe}&limit={limit}";
        var response = await _client.GetAsync<JsonElement>(endpoint, AlpacaClient.MarketData);
        
        var bars = new Dictionary<string, Bar[]>();
        if (response.TryGetProperty("bars", out var barsElement))
        {
            foreach (var prop in barsElement.EnumerateObject())
            {
                bars[prop.Name] = JsonSerializer.Deserialize<Bar[]>(prop.Value.GetRawText()) ?? [];
            }
        }
        return bars;
    }
}
