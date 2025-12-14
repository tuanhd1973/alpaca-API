"""
Alpaca Markets API Client

A comprehensive Python client for Alpaca Trading, Market Data, and Broker APIs.

Usage:
    from alpaca_client import AlpacaClient, TradingAPI, MarketDataAPI
    
    client = AlpacaClient("API_KEY", "API_SECRET", paper=True)
    trading = TradingAPI(client)
    market_data = MarketDataAPI(client)
    
    # Get account
    account = trading.get_account()
    
    # Place order
    order = trading.buy("AAPL", qty=10)
    
    # Get market data
    bars = market_data.get_stock_bars(["AAPL", "MSFT"], timeframe="1Day")
"""

from .client import AlpacaClient
from .trading import TradingAPI
from .market_data import MarketDataAPI
from .broker import BrokerAPI
from .streaming import AlpacaStream, StreamType
from .exceptions import (
    AlpacaError,
    AuthenticationError,
    ForbiddenError,
    NotFoundError,
    RateLimitError,
    ValidationError,
    InsufficientFundsError,
    MarketClosedError,
    OrderError,
    PositionError,
    APIError,
)
from .models import (
    Account,
    Asset,
    Order,
    Position,
    Clock,
    Calendar,
    Watchlist,
    Bar,
    Trade,
    Quote,
    Snapshot,
    OrderSide,
    OrderType,
    TimeInForce,
    OrderStatus,
    AssetClass,
    AssetStatus,
    AccountStatus,
    PositionSide,
)

__version__ = "1.0.0"
__author__ = "Alpaca Client"

__all__ = [
    # Core
    "AlpacaClient",
    "TradingAPI",
    "MarketDataAPI",
    "BrokerAPI",
    "AlpacaStream",
    "StreamType",
    # Exceptions
    "AlpacaError",
    "AuthenticationError",
    "ForbiddenError",
    "NotFoundError",
    "RateLimitError",
    "ValidationError",
    "InsufficientFundsError",
    "MarketClosedError",
    "OrderError",
    "PositionError",
    "APIError",
    # Models
    "Account",
    "Asset",
    "Order",
    "Position",
    "Clock",
    "Calendar",
    "Watchlist",
    "Bar",
    "Trade",
    "Quote",
    "Snapshot",
    # Enums
    "OrderSide",
    "OrderType",
    "TimeInForce",
    "OrderStatus",
    "AssetClass",
    "AssetStatus",
    "AccountStatus",
    "PositionSide",
]
