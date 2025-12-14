namespace Alpaca.Api;

public record Account(
    string Id,
    string AccountNumber,
    string Status,
    string Currency,
    decimal Cash,
    decimal BuyingPower,
    decimal PortfolioValue,
    decimal Equity,
    decimal LastEquity,
    int DaytradeCount,
    bool PatternDayTrader,
    bool TradingBlocked,
    bool TransfersBlocked,
    bool AccountBlocked,
    DateTime CreatedAt
);

public record Order(
    string Id,
    string ClientOrderId,
    DateTime CreatedAt,
    DateTime? SubmittedAt,
    DateTime? FilledAt,
    string AssetId,
    string Symbol,
    string AssetClass,
    string? Qty,
    string FilledQty,
    string? FilledAvgPrice,
    string Type,
    string Side,
    string TimeInForce,
    string? LimitPrice,
    string? StopPrice,
    string Status,
    bool ExtendedHours
);

public record Position(
    string AssetId,
    string Symbol,
    string Exchange,
    string AssetClass,
    decimal AvgEntryPrice,
    decimal Qty,
    string Side,
    decimal MarketValue,
    decimal CostBasis,
    decimal UnrealizedPl,
    decimal UnrealizedPlpc,
    decimal CurrentPrice,
    decimal LastdayPrice,
    decimal ChangeToday
);

public record Clock(
    DateTime Timestamp,
    bool IsOpen,
    DateTime NextOpen,
    DateTime NextClose
);

public record Bar(
    DateTime T,
    decimal O,
    decimal H,
    decimal L,
    decimal C,
    long V,
    int? N,
    decimal? Vw
);

public record Trade(
    DateTime T,
    decimal P,
    int S,
    string? X,
    long? I
);

public record Quote(
    DateTime T,
    decimal Ap,
    int As,
    decimal Bp,
    int Bs,
    string? Ax,
    string? Bx
);

public record OrderRequest(
    string Symbol,
    string? Qty,
    string? Notional,
    string Side,
    string Type,
    string TimeInForce,
    string? LimitPrice = null,
    string? StopPrice = null,
    bool ExtendedHours = false
);
