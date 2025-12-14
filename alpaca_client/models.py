"""
Alpaca API Response Models (Pydantic)
"""
from datetime import datetime, date
from typing import Optional, List, Dict, Any
from decimal import Decimal
from enum import Enum
from dataclasses import dataclass, field


# ========== ENUMS ==========

class OrderSide(str, Enum):
    BUY = "buy"
    SELL = "sell"


class OrderType(str, Enum):
    MARKET = "market"
    LIMIT = "limit"
    STOP = "stop"
    STOP_LIMIT = "stop_limit"
    TRAILING_STOP = "trailing_stop"


class TimeInForce(str, Enum):
    DAY = "day"
    GTC = "gtc"
    OPG = "opg"
    CLS = "cls"
    IOC = "ioc"
    FOK = "fok"


class OrderStatus(str, Enum):
    NEW = "new"
    PARTIALLY_FILLED = "partially_filled"
    FILLED = "filled"
    DONE_FOR_DAY = "done_for_day"
    CANCELED = "canceled"
    EXPIRED = "expired"
    REPLACED = "replaced"
    PENDING_CANCEL = "pending_cancel"
    PENDING_REPLACE = "pending_replace"
    PENDING_NEW = "pending_new"
    ACCEPTED = "accepted"
    STOPPED = "stopped"
    REJECTED = "rejected"
    SUSPENDED = "suspended"
    CALCULATED = "calculated"


class AssetClass(str, Enum):
    US_EQUITY = "us_equity"
    CRYPTO = "crypto"


class AssetStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"


class AccountStatus(str, Enum):
    ONBOARDING = "ONBOARDING"
    SUBMISSION_FAILED = "SUBMISSION_FAILED"
    SUBMITTED = "SUBMITTED"
    ACCOUNT_UPDATED = "ACCOUNT_UPDATED"
    APPROVAL_PENDING = "APPROVAL_PENDING"
    ACTIVE = "ACTIVE"
    REJECTED = "REJECTED"


class PositionSide(str, Enum):
    LONG = "long"
    SHORT = "short"


# ========== DATACLASSES ==========

@dataclass
class Account:
    """Trading account information."""
    id: str
    account_number: str
    status: str
    currency: str
    cash: Decimal
    buying_power: Decimal
    portfolio_value: Decimal
    equity: Decimal
    last_equity: Decimal
    long_market_value: Decimal
    short_market_value: Decimal
    initial_margin: Decimal
    maintenance_margin: Decimal
    daytrade_count: int
    pattern_day_trader: bool
    trading_blocked: bool
    transfers_blocked: bool
    account_blocked: bool
    created_at: datetime
    shorting_enabled: bool = False
    multiplier: str = "1"
    sma: Optional[Decimal] = None
    daytrading_buying_power: Optional[Decimal] = None
    regt_buying_power: Optional[Decimal] = None
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Account":
        return cls(
            id=data["id"],
            account_number=data["account_number"],
            status=data["status"],
            currency=data["currency"],
            cash=Decimal(data["cash"]),
            buying_power=Decimal(data["buying_power"]),
            portfolio_value=Decimal(data["portfolio_value"]),
            equity=Decimal(data["equity"]),
            last_equity=Decimal(data["last_equity"]),
            long_market_value=Decimal(data["long_market_value"]),
            short_market_value=Decimal(data["short_market_value"]),
            initial_margin=Decimal(data["initial_margin"]),
            maintenance_margin=Decimal(data["maintenance_margin"]),
            daytrade_count=int(data["daytrade_count"]),
            pattern_day_trader=data["pattern_day_trader"],
            trading_blocked=data["trading_blocked"],
            transfers_blocked=data["transfers_blocked"],
            account_blocked=data["account_blocked"],
            created_at=datetime.fromisoformat(data["created_at"].replace("Z", "+00:00")),
            shorting_enabled=data.get("shorting_enabled", False),
            multiplier=data.get("multiplier", "1"),
            sma=Decimal(data["sma"]) if data.get("sma") else None,
            daytrading_buying_power=Decimal(data["daytrading_buying_power"]) if data.get("daytrading_buying_power") else None,
            regt_buying_power=Decimal(data["regt_buying_power"]) if data.get("regt_buying_power") else None,
        )


@dataclass
class Asset:
    """Tradeable asset."""
    id: str
    class_: str
    exchange: str
    symbol: str
    name: str
    status: str
    tradable: bool
    marginable: bool
    shortable: bool
    easy_to_borrow: bool
    fractionable: bool
    maintenance_margin_requirement: Optional[Decimal] = None
    min_order_size: Optional[Decimal] = None
    min_trade_increment: Optional[Decimal] = None
    price_increment: Optional[Decimal] = None
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Asset":
        return cls(
            id=data["id"],
            class_=data["class"],
            exchange=data["exchange"],
            symbol=data["symbol"],
            name=data.get("name", ""),
            status=data["status"],
            tradable=data["tradable"],
            marginable=data["marginable"],
            shortable=data["shortable"],
            easy_to_borrow=data["easy_to_borrow"],
            fractionable=data.get("fractionable", False),
            maintenance_margin_requirement=Decimal(data["maintenance_margin_requirement"]) if data.get("maintenance_margin_requirement") else None,
            min_order_size=Decimal(data["min_order_size"]) if data.get("min_order_size") else None,
            min_trade_increment=Decimal(data["min_trade_increment"]) if data.get("min_trade_increment") else None,
            price_increment=Decimal(data["price_increment"]) if data.get("price_increment") else None,
        )


@dataclass
class Order:
    """Trading order."""
    id: str
    client_order_id: str
    created_at: datetime
    submitted_at: Optional[datetime]
    filled_at: Optional[datetime]
    expired_at: Optional[datetime]
    canceled_at: Optional[datetime]
    asset_id: str
    symbol: str
    asset_class: str
    qty: Optional[Decimal]
    filled_qty: Decimal
    filled_avg_price: Optional[Decimal]
    order_class: str
    order_type: str
    type: str
    side: str
    time_in_force: str
    limit_price: Optional[Decimal]
    stop_price: Optional[Decimal]
    status: str
    extended_hours: bool
    notional: Optional[Decimal] = None
    trail_percent: Optional[Decimal] = None
    trail_price: Optional[Decimal] = None
    hwm: Optional[Decimal] = None
    legs: Optional[List["Order"]] = None
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Order":
        def parse_dt(val):
            if val:
                return datetime.fromisoformat(val.replace("Z", "+00:00"))
            return None
        
        def parse_decimal(val):
            if val is not None:
                return Decimal(str(val))
            return None
        
        legs = None
        if data.get("legs"):
            legs = [Order.from_dict(leg) for leg in data["legs"]]
        
        return cls(
            id=data["id"],
            client_order_id=data["client_order_id"],
            created_at=parse_dt(data["created_at"]),
            submitted_at=parse_dt(data.get("submitted_at")),
            filled_at=parse_dt(data.get("filled_at")),
            expired_at=parse_dt(data.get("expired_at")),
            canceled_at=parse_dt(data.get("canceled_at")),
            asset_id=data["asset_id"],
            symbol=data["symbol"],
            asset_class=data["asset_class"],
            qty=parse_decimal(data.get("qty")),
            filled_qty=Decimal(data.get("filled_qty", "0")),
            filled_avg_price=parse_decimal(data.get("filled_avg_price")),
            order_class=data.get("order_class", ""),
            order_type=data.get("order_type", data.get("type", "")),
            type=data.get("type", ""),
            side=data["side"],
            time_in_force=data["time_in_force"],
            limit_price=parse_decimal(data.get("limit_price")),
            stop_price=parse_decimal(data.get("stop_price")),
            status=data["status"],
            extended_hours=data.get("extended_hours", False),
            notional=parse_decimal(data.get("notional")),
            trail_percent=parse_decimal(data.get("trail_percent")),
            trail_price=parse_decimal(data.get("trail_price")),
            hwm=parse_decimal(data.get("hwm")),
            legs=legs,
        )
    
    @property
    def is_filled(self) -> bool:
        return self.status == OrderStatus.FILLED.value
    
    @property
    def is_open(self) -> bool:
        return self.status in [
            OrderStatus.NEW.value,
            OrderStatus.PARTIALLY_FILLED.value,
            OrderStatus.ACCEPTED.value,
            OrderStatus.PENDING_NEW.value,
        ]
    
    @property
    def is_canceled(self) -> bool:
        return self.status in [
            OrderStatus.CANCELED.value,
            OrderStatus.EXPIRED.value,
            OrderStatus.REJECTED.value,
        ]


@dataclass
class Position:
    """Open position."""
    asset_id: str
    symbol: str
    exchange: str
    asset_class: str
    avg_entry_price: Decimal
    qty: Decimal
    side: str
    market_value: Decimal
    cost_basis: Decimal
    unrealized_pl: Decimal
    unrealized_plpc: Decimal
    unrealized_intraday_pl: Decimal
    unrealized_intraday_plpc: Decimal
    current_price: Decimal
    lastday_price: Decimal
    change_today: Decimal
    qty_available: Optional[Decimal] = None
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Position":
        return cls(
            asset_id=data["asset_id"],
            symbol=data["symbol"],
            exchange=data["exchange"],
            asset_class=data["asset_class"],
            avg_entry_price=Decimal(data["avg_entry_price"]),
            qty=Decimal(data["qty"]),
            side=data["side"],
            market_value=Decimal(data["market_value"]),
            cost_basis=Decimal(data["cost_basis"]),
            unrealized_pl=Decimal(data["unrealized_pl"]),
            unrealized_plpc=Decimal(data["unrealized_plpc"]),
            unrealized_intraday_pl=Decimal(data["unrealized_intraday_pl"]),
            unrealized_intraday_plpc=Decimal(data["unrealized_intraday_plpc"]),
            current_price=Decimal(data["current_price"]),
            lastday_price=Decimal(data["lastday_price"]),
            change_today=Decimal(data["change_today"]),
            qty_available=Decimal(data["qty_available"]) if data.get("qty_available") else None,
        )
    
    @property
    def profit_loss(self) -> Decimal:
        return self.unrealized_pl
    
    @property
    def profit_loss_percent(self) -> Decimal:
        return self.unrealized_plpc * 100


@dataclass
class Clock:
    """Market clock."""
    timestamp: datetime
    is_open: bool
    next_open: datetime
    next_close: datetime
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Clock":
        def parse_dt(val):
            return datetime.fromisoformat(val.replace("Z", "+00:00"))
        
        return cls(
            timestamp=parse_dt(data["timestamp"]),
            is_open=data["is_open"],
            next_open=parse_dt(data["next_open"]),
            next_close=parse_dt(data["next_close"]),
        )


@dataclass
class Calendar:
    """Market calendar day."""
    date: date
    open: str
    close: str
    session_open: Optional[str] = None
    session_close: Optional[str] = None
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Calendar":
        return cls(
            date=date.fromisoformat(data["date"]),
            open=data["open"],
            close=data["close"],
            session_open=data.get("session_open"),
            session_close=data.get("session_close"),
        )


@dataclass
class Watchlist:
    """Watchlist."""
    id: str
    account_id: str
    name: str
    created_at: datetime
    updated_at: datetime
    assets: List[Asset] = field(default_factory=list)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Watchlist":
        def parse_dt(val):
            return datetime.fromisoformat(val.replace("Z", "+00:00"))
        
        assets = []
        if data.get("assets"):
            assets = [Asset.from_dict(a) for a in data["assets"]]
        
        return cls(
            id=data["id"],
            account_id=data["account_id"],
            name=data["name"],
            created_at=parse_dt(data["created_at"]),
            updated_at=parse_dt(data["updated_at"]),
            assets=assets,
        )


@dataclass
class Bar:
    """OHLCV bar."""
    timestamp: datetime
    open: Decimal
    high: Decimal
    low: Decimal
    close: Decimal
    volume: int
    trade_count: Optional[int] = None
    vwap: Optional[Decimal] = None
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Bar":
        return cls(
            timestamp=datetime.fromisoformat(data["t"].replace("Z", "+00:00")),
            open=Decimal(str(data["o"])),
            high=Decimal(str(data["h"])),
            low=Decimal(str(data["l"])),
            close=Decimal(str(data["c"])),
            volume=int(data["v"]),
            trade_count=data.get("n"),
            vwap=Decimal(str(data["vw"])) if data.get("vw") else None,
        )


@dataclass
class Trade:
    """Trade tick."""
    timestamp: datetime
    price: Decimal
    size: float
    exchange: Optional[str] = None
    id: Optional[int] = None
    conditions: List[str] = field(default_factory=list)
    tape: Optional[str] = None
    taker_side: Optional[str] = None  # For crypto: 'B' or 'S'
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Trade":
        return cls(
            timestamp=datetime.fromisoformat(data["t"].replace("Z", "+00:00")),
            price=Decimal(str(data["p"])),
            size=float(data["s"]),
            exchange=data.get("x"),
            id=data.get("i"),
            conditions=data.get("c", []),
            tape=data.get("z"),
            taker_side=data.get("tks"),
        )


@dataclass
class Quote:
    """Quote tick."""
    timestamp: datetime
    ask_price: Decimal
    ask_size: float
    bid_price: Decimal
    bid_size: float
    ask_exchange: Optional[str] = None
    bid_exchange: Optional[str] = None
    conditions: List[str] = field(default_factory=list)
    tape: Optional[str] = None
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Quote":
        return cls(
            timestamp=datetime.fromisoformat(data["t"].replace("Z", "+00:00")),
            ask_price=Decimal(str(data["ap"])),
            ask_size=float(data["as"]),
            bid_price=Decimal(str(data["bp"])),
            bid_size=float(data["bs"]),
            ask_exchange=data.get("ax"),
            bid_exchange=data.get("bx"),
            conditions=data.get("c", []),
            tape=data.get("z"),
        )
    
    @property
    def spread(self) -> Decimal:
        return self.ask_price - self.bid_price
    
    @property
    def mid_price(self) -> Decimal:
        return (self.ask_price + self.bid_price) / 2


@dataclass 
class Snapshot:
    """Market snapshot."""
    symbol: str
    latest_trade: Optional[Trade] = None
    latest_quote: Optional[Quote] = None
    minute_bar: Optional[Bar] = None
    daily_bar: Optional[Bar] = None
    prev_daily_bar: Optional[Bar] = None
    
    @classmethod
    def from_dict(cls, symbol: str, data: Dict[str, Any]) -> "Snapshot":
        return cls(
            symbol=symbol,
            latest_trade=Trade.from_dict(data["latestTrade"]) if data.get("latestTrade") else None,
            latest_quote=Quote.from_dict(data["latestQuote"]) if data.get("latestQuote") else None,
            minute_bar=Bar.from_dict(data["minuteBar"]) if data.get("minuteBar") else None,
            daily_bar=Bar.from_dict(data["dailyBar"]) if data.get("dailyBar") else None,
            prev_daily_bar=Bar.from_dict(data["prevDailyBar"]) if data.get("prevDailyBar") else None,
        )
