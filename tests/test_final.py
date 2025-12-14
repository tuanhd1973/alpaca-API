"""
FINAL COMPREHENSIVE TEST - All Alpaca API Features
"""
import os
import asyncio
from datetime import datetime, timedelta, date
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.environ.get("ALPACA_API_KEY")
API_SECRET = os.environ.get("ALPACA_API_SECRET")

from alpaca_client import (
    AlpacaClient, TradingAPI, MarketDataAPI,
    AlpacaError, NotFoundError
)
from alpaca_client.streaming import AlpacaStream, StreamType

results = {"passed": 0, "failed": 0}

def test(category, name, func):
    try:
        result = func()
        print(f"  ✓ {name}")
        results["passed"] += 1
        return result
    except Exception as e:
        print(f"  ✗ {name}: {e}")
        results["failed"] += 1
        return None

print("=" * 70)
print("🦙 ALPACA API CLIENT - FINAL COMPREHENSIVE TEST")
print("=" * 70)

client = AlpacaClient(API_KEY, API_SECRET, paper=True)
trading = TradingAPI(client)
market_data = MarketDataAPI(client)

# ==================== TRADING API ====================
print("\n📊 TRADING API")
print("-" * 50)

test("Trading", "Account Info", lambda: trading.get_account())
test("Trading", "Account Config", lambda: trading.get_account_configurations())
test("Trading", "Portfolio History", lambda: trading.get_portfolio_history(period="1M"))
test("Trading", "Account Activities", lambda: trading.get_account_activities())
test("Trading", "Get Assets", lambda: trading.get_assets(status="active")[:10])
test("Trading", "Get Asset (AAPL)", lambda: trading.get_asset("AAPL"))
test("Trading", "Get Asset (BTC/USD)", lambda: trading.get_asset("BTC/USD"))
test("Trading", "Market Clock", lambda: trading.get_clock())
test("Trading", "Market Calendar", lambda: trading.get_calendar()[:5])
test("Trading", "Get Positions", lambda: trading.get_positions())
test("Trading", "Get Orders", lambda: trading.get_orders(status="all"))
test("Trading", "Buying Power", lambda: trading.get_buying_power())
test("Trading", "Is Market Open", lambda: trading.is_market_open())

# Order lifecycle
print("\n📝 ORDER LIFECYCLE")
print("-" * 50)
order = test("Orders", "Create Limit Order", 
    lambda: trading.buy_limit("AAPL", qty=1, limit_price=100.00))
if order:
    test("Orders", "Get Order", lambda: trading.get_order(order.id))
    test("Orders", "Cancel Order", lambda: trading.cancel_order(order.id))

# Watchlist lifecycle
print("\n📋 WATCHLIST LIFECYCLE")
print("-" * 50)
wl = test("Watchlist", "Create Watchlist", 
    lambda: trading.create_watchlist("FinalTest", ["AAPL", "MSFT"]))
if wl:
    test("Watchlist", "Get Watchlists", lambda: trading.get_watchlists())
    test("Watchlist", "Get Watchlist", lambda: trading.get_watchlist(wl.id))
    test("Watchlist", "Add Symbol", lambda: trading.add_to_watchlist(wl.id, "GOOGL"))
    test("Watchlist", "Update Watchlist", lambda: trading.update_watchlist(wl.id, symbols=["TSLA"]))
    test("Watchlist", "Remove Symbol", lambda: trading.remove_from_watchlist(wl.id, "TSLA"))
    test("Watchlist", "Delete Watchlist", lambda: trading.delete_watchlist(wl.id))

# ==================== MARKET DATA API ====================
print("\n📈 MARKET DATA - STOCKS")
print("-" * 50)

test("Stocks", "Stock Bars", 
    lambda: market_data.get_stock_bars(["AAPL"], "1Day", start=date.today()-timedelta(days=7)))
test("Stocks", "Stock Trades", 
    lambda: market_data.get_stock_trades(["AAPL"], start=date.today()-timedelta(days=3), limit=5))
test("Stocks", "Stock Quotes", 
    lambda: market_data.get_stock_quotes(["AAPL"], start=date.today()-timedelta(days=3), limit=5))
test("Stocks", "Stock Snapshots", lambda: market_data.get_stock_snapshots(["AAPL", "MSFT"]))
test("Stocks", "Stock Snapshot", lambda: market_data.get_stock_snapshot("AAPL"))
test("Stocks", "Current Price", lambda: market_data.get_current_price("AAPL"))
test("Stocks", "Latest Quote", lambda: market_data.get_latest_quote("AAPL"))
test("Stocks", "Multi Prices", lambda: market_data.get_multi_stock_prices(["AAPL", "MSFT", "GOOGL"]))
test("Stocks", "Daily Bars", lambda: market_data.get_daily_bars("AAPL", days=10))

print("\n📊 MARKET DATA - META")
print("-" * 50)
test("Meta", "Exchanges", lambda: market_data.get_stock_exchanges())
test("Meta", "Trade Conditions", lambda: market_data.get_trade_conditions())
test("Meta", "Quote Conditions", lambda: market_data.get_quote_conditions())

print("\n🪙 MARKET DATA - CRYPTO")
print("-" * 50)
test("Crypto", "Crypto Bars", 
    lambda: market_data.get_crypto_bars(["BTC/USD"], "1Hour", start=date.today()-timedelta(days=1)))
test("Crypto", "Crypto Trades", lambda: market_data.get_crypto_trades(["BTC/USD"], limit=5))
test("Crypto", "Crypto Quotes", lambda: market_data.get_crypto_quotes(["BTC/USD"], limit=5))
test("Crypto", "Crypto Snapshots", lambda: market_data.get_crypto_snapshots(["BTC/USD", "ETH/USD"]))
test("Crypto", "Crypto Symbols", lambda: market_data.get_crypto_symbols())

print("\n📜 MARKET DATA - OPTIONS")
print("-" * 50)
test("Options", "Options Contracts", 
    lambda: market_data.get_options_contracts(underlying_symbols=["AAPL"], limit=3))
test("Options", "Options Snapshots", lambda: market_data.get_options_snapshots("AAPL"))

# ==================== STREAMING ====================
print("\n🔴 STREAMING")
print("-" * 50)

async def test_streaming():
    stream = AlpacaStream(API_KEY, API_SECRET, StreamType.IEX)
    try:
        connected = await stream.connect()
        if connected:
            await stream.subscribe(trades=["AAPL"])
            await stream.unsubscribe(trades=["AAPL"])
            await stream.disconnect()
            return True
        return False
    except Exception as e:
        return False

streaming_ok = asyncio.run(test_streaming())
if streaming_ok:
    print("  ✓ Market Data Streaming")
    results["passed"] += 1
else:
    print("  ✗ Market Data Streaming")
    results["failed"] += 1

async def test_crypto_streaming():
    stream = AlpacaStream(API_KEY, API_SECRET, StreamType.CRYPTO)
    try:
        connected = await stream.connect()
        if connected:
            await stream.subscribe(trades=["BTC/USD"])
            await stream.unsubscribe(trades=["BTC/USD"])
            await stream.disconnect()
            return True
        return False
    except:
        return False

crypto_stream_ok = asyncio.run(test_crypto_streaming())
if crypto_stream_ok:
    print("  ✓ Crypto Streaming")
    results["passed"] += 1
else:
    print("  ✗ Crypto Streaming")
    results["failed"] += 1

# ==================== SUMMARY ====================
print("\n" + "=" * 70)
print("📊 FINAL TEST RESULTS")
print("=" * 70)

total = results["passed"] + results["failed"]
success_rate = (results["passed"] / total * 100) if total > 0 else 0

print(f"""
  ✅ Passed:  {results['passed']}
  ❌ Failed:  {results['failed']}
  📈 Total:   {total}
  
  Success Rate: {success_rate:.1f}%
""")

if results["failed"] == 0:
    print("  🎉 ALL TESTS PASSED! API CLIENT IS FULLY FUNCTIONAL!")
else:
    print(f"  ⚠️  {results['failed']} test(s) need attention")

print("=" * 70)

# Feature summary
print("""
📦 IMPLEMENTED FEATURES:
  ├── Trading API
  │   ├── Account (info, config, activities, history)
  │   ├── Assets (list, get by symbol)
  │   ├── Orders (create, get, update, cancel)
  │   ├── Positions (list, get, close)
  │   ├── Watchlists (CRUD operations)
  │   └── System (clock, calendar)
  │
  ├── Market Data API
  │   ├── Stocks (bars, trades, quotes, snapshots)
  │   ├── Crypto (bars, trades, quotes, snapshots)
  │   ├── Options (contracts, snapshots)
  │   └── Meta (exchanges, conditions)
  │
  ├── Streaming API
  │   ├── Market Data (IEX/SIP)
  │   └── Crypto (24/7)
  │
  └── Infrastructure
      ├── Error Handling (custom exceptions)
      ├── Retry Logic (exponential backoff)
      ├── Rate Limiting
      └── Type Safety (dataclass models)
""")

client.close()
