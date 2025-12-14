using System.Net.Http.Headers;
using System.Text;
using System.Text.Json;

namespace Alpaca.Api;

public class AlpacaClientOptions
{
    public required string ApiKey { get; set; }
    public required string ApiSecret { get; set; }
    public bool Paper { get; set; } = true;
    public TimeSpan Timeout { get; set; } = TimeSpan.FromSeconds(30);
}

public class AlpacaClient : IDisposable
{
    public const string TradingLive = "https://api.alpaca.markets";
    public const string TradingPaper = "https://paper-api.alpaca.markets";
    public const string MarketData = "https://data.alpaca.markets";

    private readonly HttpClient _client;
    private readonly string _baseUrl;

    public AlpacaClient(AlpacaClientOptions options)
    {
        _baseUrl = options.Paper ? TradingPaper : TradingLive;
        
        _client = new HttpClient { Timeout = options.Timeout };
        _client.DefaultRequestHeaders.Add("APCA-API-KEY-ID", options.ApiKey);
        _client.DefaultRequestHeaders.Add("APCA-API-SECRET-KEY", options.ApiSecret);
        _client.DefaultRequestHeaders.Accept.Add(new MediaTypeWithQualityHeaderValue("application/json"));
    }

    public async Task<T> GetAsync<T>(string endpoint, string? baseUrl = null)
    {
        var url = (baseUrl ?? _baseUrl) + endpoint;
        var response = await _client.GetAsync(url);
        response.EnsureSuccessStatusCode();
        var json = await response.Content.ReadAsStringAsync();
        return JsonSerializer.Deserialize<T>(json, JsonOptions)!;
    }

    public async Task<T> PostAsync<T>(string endpoint, object? body = null)
    {
        var url = _baseUrl + endpoint;
        var content = body != null 
            ? new StringContent(JsonSerializer.Serialize(body, JsonOptions), Encoding.UTF8, "application/json")
            : null;
        var response = await _client.PostAsync(url, content);
        response.EnsureSuccessStatusCode();
        var json = await response.Content.ReadAsStringAsync();
        return JsonSerializer.Deserialize<T>(json, JsonOptions)!;
    }

    public async Task DeleteAsync(string endpoint)
    {
        var url = _baseUrl + endpoint;
        var response = await _client.DeleteAsync(url);
        response.EnsureSuccessStatusCode();
    }

    private static readonly JsonSerializerOptions JsonOptions = new()
    {
        PropertyNamingPolicy = JsonNamingPolicy.SnakeCaseLower,
        PropertyNameCaseInsensitive = true
    };

    public void Dispose() => _client.Dispose();
}
