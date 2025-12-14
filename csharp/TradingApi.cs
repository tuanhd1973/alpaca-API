namespace Alpaca.Api;

public class TradingApi
{
    private readonly AlpacaClient _client;

    public TradingApi(AlpacaClient client) => _client = client;

    // Account
    public Task<Account> GetAccountAsync() => _client.GetAsync<Account>("/v2/account");

    public async Task<decimal> GetBuyingPowerAsync()
    {
        var account = await GetAccountAsync();
        return account.BuyingPowerDecimal;
    }

    // Orders
    public Task<Order> CreateOrderAsync(OrderRequest request) =>
        _client.PostAsync<Order>("/v2/orders", request);

    public Task<Order> BuyAsync(string symbol, int qty) =>
        CreateOrderAsync(new OrderRequest(symbol.ToUpper(), qty.ToString(), null, "buy", "market", "day"));

    public Task<Order> SellAsync(string symbol, int qty) =>
        CreateOrderAsync(new OrderRequest(symbol.ToUpper(), qty.ToString(), null, "sell", "market", "day"));

    public Task<Order> BuyLimitAsync(string symbol, int qty, decimal limitPrice) =>
        CreateOrderAsync(new OrderRequest(symbol.ToUpper(), qty.ToString(), null, "buy", "limit", "gtc", limitPrice.ToString()));

    public Task<Order[]> GetOrdersAsync() => _client.GetAsync<Order[]>("/v2/orders");

    public Task<Order> GetOrderAsync(string orderId) => _client.GetAsync<Order>($"/v2/orders/{orderId}");

    public Task CancelOrderAsync(string orderId) => _client.DeleteAsync($"/v2/orders/{orderId}");

    public Task CancelAllOrdersAsync() => _client.DeleteAsync("/v2/orders");

    // Positions
    public Task<Position[]> GetPositionsAsync() => _client.GetAsync<Position[]>("/v2/positions");

    public Task<Position> GetPositionAsync(string symbol) => 
        _client.GetAsync<Position>($"/v2/positions/{symbol.ToUpper()}");

    // Clock
    public Task<Clock> GetClockAsync() => _client.GetAsync<Clock>("/v2/clock");

    public async Task<bool> IsMarketOpenAsync()
    {
        var clock = await GetClockAsync();
        return clock.IsOpen;
    }
}
