"""
Alpaca API Client - Comprehensive Usage Examples
"""
import os
from datetime import datetime, timedelta
from decimal import Decimal

from dotenv import load_dotenv

from alpaca_client import (
    AlpacaClient,
    TradingAPI,
    MarketDataAPI,
    OrderSide,
    OrderType,
    TimeInForce,
    AlpacaError,
    NotFoundError,
    ValidationError,
)

# Load .env file if exists
load_dotenv()

API_KEY = os.environ.get("ALPACA_API_KEY")
API_SECRET = os.environ.get("ALPACA_API_SECRET")


def main():
    if not API_KEY or not API_SECRET:
        print("Error: Set ALPACA_API_KEY and ALPACA_API_SECRET environment variables")
        return
    
    # ==================== SETUP ====================
    
    # Initialize client (paper trading by default)
    client = AlpacaClient(
        api_key=API_KEY,
        api_secret=API_SECRET,
        paper=True,  # Use paper trading
        timeout=30,
        max_retries=3,
    )
    
    # Initialize APIs
    trading = TradingAPI(client)
    market_data = MarketDataAPI(client)
    
    # ==================== ACCOUNT ====================
    
    # Get account info
    account = trading.get_account()
    print(f"Account ID: {account.id}")
    print(f"Buying Power: ${account.buying_power:,.2f}")
    print(f"Portfolio Value: ${account.portfolio_value:,.2f}")
    print(f"Cash: ${account.cash:,.2f}")
    print(f"Day Trade Count: {account.daytrade_count}")
    print(f"Pattern Day Trader: {account.pattern_day_trader}")
    
    # Check market status
    clock = trading.get_clock()
    print(f"\nMarket Open: {clock.is_open}")
    print(f"Next Open: {clock.next_open}")
    print(f"Next Close: {clock.next_close}")
    
    # ==================== MARKET DATA ====================
    
    # Get current price
    try:
        price = market_data.get_current_price("AAPL")
        print(f"\nAAPL Current Price: ${price}")
    except Exception as e:
        print(f"Could not get price: {e}")
    
    # Get multiple stock prices
    prices = market_data.get_multi_stock_prices(["AAPL", "MSFT", "GOOGL"])
    print("\nCurrent Prices:")
    for symbol, price in prices.items():
        print(f"  {symbol}: ${price}")
    
    # Get historical bars
    bars = market_data.get_all_stock_bars(
        symbols=["AAPL"],
        timeframe="1Day",
        start=datetime.now() - timedelta(days=30),
        adjustment="split",
    )
    
    print(f"\nAAPL Last 5 Days:")
    for bar in bars.get("AAPL", [])[-5:]:
        print(f"  {bar.timestamp.date()}: O={bar.open} H={bar.high} L={bar.low} C={bar.close} V={bar.volume}")
    
    # Get snapshot
    snapshot = market_data.get_stock_snapshot("AAPL")
    if snapshot.latest_quote:
        print(f"\nAAPL Quote: Bid=${snapshot.latest_quote.bid_price} Ask=${snapshot.latest_quote.ask_price}")
        print(f"  Spread: ${snapshot.latest_quote.spread}")

    # ==================== ORDERS ====================
    
    # Simple market buy
    try:
        order = trading.buy("AAPL", qty=1)
        print(f"\nMarket Buy Order: {order.id}")
        print(f"  Status: {order.status}")
        print(f"  Symbol: {order.symbol}")
        print(f"  Qty: {order.qty}")
    except ValidationError as e:
        print(f"Validation error: {e}")
    except AlpacaError as e:
        print(f"Order failed: {e}")
    
    # Limit order
    try:
        order = trading.buy_limit(
            symbol="MSFT",
            qty=5,
            limit_price=350.00,
            time_in_force=TimeInForce.GTC,
        )
        print(f"\nLimit Buy Order: {order.id}")
        print(f"  Limit Price: ${order.limit_price}")
    except AlpacaError as e:
        print(f"Order failed: {e}")
    
    # Dollar-based order (fractional shares)
    try:
        order = trading.buy("GOOGL", notional=500)  # Buy $500 worth
        print(f"\nNotional Order: {order.id}")
    except AlpacaError as e:
        print(f"Order failed: {e}")
    
    # Bracket order (entry + take profit + stop loss)
    try:
        order = trading.bracket_order(
            symbol="AAPL",
            side=OrderSide.BUY,
            qty=10,
            take_profit_price=200.00,
            stop_loss_price=150.00,
        )
        print(f"\nBracket Order: {order.id}")
        if order.legs:
            for leg in order.legs:
                print(f"  Leg: {leg.type} @ {leg.limit_price or leg.stop_price}")
    except AlpacaError as e:
        print(f"Order failed: {e}")
    
    # Get open orders
    open_orders = trading.get_open_orders()
    print(f"\nOpen Orders: {len(open_orders)}")
    for order in open_orders[:5]:
        print(f"  {order.symbol}: {order.side} {order.qty} @ {order.type}")
    
    # Cancel all orders
    # trading.cancel_all_orders()
    
    # ==================== POSITIONS ====================
    
    positions = trading.get_positions()
    print(f"\nPositions: {len(positions)}")
    
    total_pl = Decimal(0)
    for pos in positions:
        print(f"  {pos.symbol}:")
        print(f"    Qty: {pos.qty} @ ${pos.avg_entry_price}")
        print(f"    Market Value: ${pos.market_value}")
        print(f"    P/L: ${pos.unrealized_pl} ({pos.profit_loss_percent:.2f}%)")
        total_pl += pos.unrealized_pl
    
    print(f"\nTotal Unrealized P/L: ${total_pl}")
    
    # Check specific position
    try:
        aapl_pos = trading.get_position("AAPL")
        print(f"\nAAPL Position: {aapl_pos.qty} shares")
    except NotFoundError:
        print("\nNo AAPL position")
    
    # Close position (partial)
    # trading.close_position("AAPL", qty=5)  # Close 5 shares
    # trading.close_position("AAPL", percentage=50)  # Close 50%
    
    # ==================== WATCHLISTS ====================
    
    # Create watchlist
    try:
        watchlist = trading.create_watchlist(
            name="Tech Stocks",
            symbols=["AAPL", "MSFT", "GOOGL", "AMZN", "META"]
        )
        print(f"\nCreated Watchlist: {watchlist.name} ({watchlist.id})")
        
        # Add symbol
        watchlist = trading.add_to_watchlist(watchlist.id, "NVDA")
        print(f"Added NVDA to watchlist")
        
        # List watchlists
        watchlists = trading.get_watchlists()
        print(f"\nWatchlists: {len(watchlists)}")
        for wl in watchlists:
            print(f"  {wl.name}: {len(wl.assets)} symbols")
    except AlpacaError as e:
        print(f"Watchlist error: {e}")

    # ==================== CRYPTO ====================
    
    # Get crypto prices
    try:
        btc_price = market_data.get_crypto_price("BTC/USD")
        print(f"\nBTC/USD: ${btc_price:,.2f}")
        
        # Get crypto bars
        crypto_bars = market_data.get_crypto_bars(
            symbols=["BTC/USD", "ETH/USD"],
            timeframe="1Hour",
            start=datetime.now() - timedelta(days=1),
        )
        print(f"Crypto bars retrieved: {list(crypto_bars.get('bars', {}).keys())}")
    except Exception as e:
        print(f"Crypto data error: {e}")
    
    # ==================== OPTIONS ====================
    
    # Get options contracts
    try:
        contracts = market_data.get_options_contracts(
            underlying_symbols=["AAPL"],
            type="call",
            expiration_date_gte=datetime.now().date(),
            strike_price_gte=150,
            strike_price_lte=200,
            limit=10,
        )
        
        print(f"\nAAPL Call Options:")
        for contract in contracts.get("option_contracts", [])[:5]:
            print(f"  {contract['symbol']}: Strike ${contract['strike_price']} Exp {contract['expiration_date']}")
    except Exception as e:
        print(f"Options error: {e}")
    
    # ==================== PORTFOLIO HISTORY ====================
    
    history = trading.get_portfolio_history(
        period="1M",
        timeframe="1D",
    )
    
    print(f"\nPortfolio History (1 Month):")
    print(f"  Data points: {len(history.get('equity', []))}")
    if history.get('equity'):
        print(f"  Start: ${history['equity'][0]:,.2f}")
        print(f"  End: ${history['equity'][-1]:,.2f}")
    
    # ==================== CLEANUP ====================
    
    # Close client session
    client.close()
    print("\nDone!")


if __name__ == "__main__":
    main()
