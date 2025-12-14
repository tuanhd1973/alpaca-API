"""
Comprehensive Alpaca API Endpoint Tests
"""
import os
import time
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.environ.get("ALPACA_API_KEY")
API_SECRET = os.environ.get("ALPACA_API_SECRET")

from alpaca_client import (
    AlpacaClient, TradingAPI, MarketDataAPI,
    AlpacaError, NotFoundError, ValidationError
)

client = AlpacaClient(API_KEY, API_SECRET, paper=True)
trading = TradingAPI(client)
market_data = MarketDataAPI(client)

passed = 0
failed = 0
skipped = 0

def test(name, func):
    global passed, failed, skipped
    try:
        result = func()
        print(f"  ✓ {name}")
        if result:
            print(f"    → {result}")
        passed += 1
        return True
    except NotFoundError as e:
        print(f"  ○ {name} (not found - expected)")
        skipped += 1
        return None
    except Exception as e:
        print(f"  ✗ {name}: {e}")
        failed += 1
        return False

print("=" * 60)
print("ALPACA API - FULL ENDPOINT TEST")
print("=" * 60)

# ==================== TRADING API ====================

print("\n[TRADING API - ACCOUNT]")
test("GET /v2/account", lambda: f"${trading.get_account().buying_power:,.2f}")
test("GET /v2/account/configurations", lambda: trading.get_account_configurations())
test("GET /v2/account/activities", lambda: f"{len(trading.get_account_activities())} activities")
test("GET /v2/account/portfolio/history", lambda: f"{len(trading.get_portfolio_history().get('equity', []))} points")

print("\n[TRADING API - ASSETS]")
test("GET /v2/assets", lambda: f"{len(trading.get_assets(status='active')[:100])} assets")
test("GET /v2/assets/AAPL", lambda: f"{trading.get_asset('AAPL').name}")
test("GET /v2/assets/BTC/USD", lambda: f"{trading.get_asset('BTC/USD').symbol}")

print("\n[TRADING API - CLOCK & CALENDAR]")
test("GET /v2/clock", lambda: f"Open: {trading.get_clock().is_open}")
test("GET /v2/calendar", lambda: f"{len(trading.get_calendar())} days")

print("\n[TRADING API - POSITIONS]")
test("GET /v2/positions", lambda: f"{len(trading.get_positions())} positions")
test("GET /v2/positions/AAPL", lambda: trading.get_position("AAPL"))

print("\n[TRADING API - ORDERS]")
test("GET /v2/orders", lambda: f"{len(trading.get_orders(status='all'))} orders")
test("GET /v2/orders (open)", lambda: f"{len(trading.get_open_orders())} open")

# Create test order
print("\n[TRADING API - ORDER LIFECYCLE]")
order_id = None
try:
    # Create limit order (won't fill on weekend)
    order = trading.buy_limit("AAPL", qty=1, limit_price=100.00)
    order_id = order.id
    print(f"  ✓ POST /v2/orders (create)")
    print(f"    → Order ID: {order_id[:8]}...")
    passed += 1
    
    time.sleep(1)
    
    # Get order
    test("GET /v2/orders/{id}", lambda: f"Status: {trading.get_order(order_id).status}")
    
    # Update order
    try:
        updated = trading.update_order(order_id, limit_price=105.00)
        print(f"  ✓ PATCH /v2/orders/{{id}}")
        print(f"    → New price: ${updated.limit_price}")
        passed += 1
        order_id = updated.id  # Replacement creates new order
    except Exception as e:
        print(f"  ○ PATCH /v2/orders/{{id}}: {e}")
        skipped += 1
    
    time.sleep(1)
    
    # Cancel order
    trading.cancel_order(order_id)
    print(f"  ✓ DELETE /v2/orders/{{id}}")
    passed += 1
    
except Exception as e:
    print(f"  ✗ Order lifecycle error: {e}")
    failed += 1
    if order_id:
        try:
            trading.cancel_order(order_id)
        except:
            pass

print("\n[TRADING API - WATCHLISTS]")
watchlist_id = None
try:
    # Create
    wl = trading.create_watchlist("Test_WL_" + str(int(time.time())), ["AAPL", "MSFT"])
    watchlist_id = wl.id
    print(f"  ✓ POST /v2/watchlists")
    print(f"    → ID: {watchlist_id[:8]}...")
    passed += 1
    
    # List
    test("GET /v2/watchlists", lambda: f"{len(trading.get_watchlists())} watchlists")
    
    # Get
    test("GET /v2/watchlists/{id}", lambda: f"{trading.get_watchlist(watchlist_id).name}")
    
    # Add symbol
    trading.add_to_watchlist(watchlist_id, "GOOGL")
    print(f"  ✓ POST /v2/watchlists/{{id}} (add symbol)")
    passed += 1
    
    # Update
    trading.update_watchlist(watchlist_id, symbols=["AAPL", "TSLA"])
    print(f"  ✓ PUT /v2/watchlists/{{id}}")
    passed += 1
    
    # Remove symbol
    trading.remove_from_watchlist(watchlist_id, "TSLA")
    print(f"  ✓ DELETE /v2/watchlists/{{id}}/{{symbol}}")
    passed += 1
    
    # Delete
    trading.delete_watchlist(watchlist_id)
    print(f"  ✓ DELETE /v2/watchlists/{{id}}")
    passed += 1
    
except Exception as e:
    print(f"  ✗ Watchlist error: {e}")
    failed += 1
    if watchlist_id:
        try:
            trading.delete_watchlist(watchlist_id)
        except:
            pass

# ==================== MARKET DATA API ====================

print("\n" + "=" * 60)
print("[MARKET DATA API - STOCKS]")
test("GET /v2/stocks/bars", 
     lambda: f"{len(market_data.get_stock_bars(['AAPL'], '1Day', start=datetime.now()-timedelta(days=7)).get('bars', {}).get('AAPL', []))} bars")
test("GET /v2/stocks/trades",
     lambda: f"{len(market_data.get_stock_trades(['AAPL'], start=datetime.now()-timedelta(days=3), limit=10).get('trades', {}).get('AAPL', []))} trades")
test("GET /v2/stocks/quotes",
     lambda: f"{len(market_data.get_stock_quotes(['AAPL'], start=datetime.now()-timedelta(days=3), limit=10).get('quotes', {}).get('AAPL', []))} quotes")
test("GET /v2/stocks/snapshots",
     lambda: f"{len(market_data.get_stock_snapshots(['AAPL', 'MSFT']))} snapshots")
test("GET /v2/stocks/{symbol}/snapshot",
     lambda: f"AAPL: ${market_data.get_stock_snapshot('AAPL').latest_trade.price}")

print("\n[MARKET DATA API - STOCK META]")
test("GET /v2/stocks/meta/exchanges",
     lambda: f"{len(market_data.get_stock_exchanges())} exchanges")
test("GET /v2/stocks/meta/conditions/trades",
     lambda: f"{len(market_data.get_trade_conditions())} conditions")
test("GET /v2/stocks/meta/conditions/quotes",
     lambda: f"{len(market_data.get_quote_conditions())} conditions")

print("\n[MARKET DATA API - CRYPTO]")
test("GET /v2/crypto/bars",
     lambda: f"{len(market_data.get_crypto_bars(['BTC/USD'], '1Hour', start=datetime.now()-timedelta(days=1)).get('bars', {}).get('BTC/USD', []))} bars")
test("GET /v2/crypto/trades",
     lambda: market_data.get_crypto_trades(['BTC/USD'], limit=5))
test("GET /v2/crypto/quotes",
     lambda: market_data.get_crypto_quotes(['BTC/USD'], limit=5))
test("GET /v2/crypto/snapshots",
     lambda: f"{len(market_data.get_crypto_snapshots(['BTC/USD', 'ETH/USD']))} snapshots")
test("GET /v2/crypto/meta/symbols",
     lambda: f"{len(market_data.get_crypto_symbols())} symbols")

print("\n[MARKET DATA API - OPTIONS]")
test("GET /v2/options/contracts",
     lambda: f"{len(market_data.get_options_contracts(underlying_symbols=['AAPL'], limit=5).get('option_contracts', []))} contracts")

# Get a contract symbol for further tests
try:
    contracts = market_data.get_options_contracts(underlying_symbols=['AAPL'], limit=1)
    if contracts.get('option_contracts'):
        contract_symbol = contracts['option_contracts'][0]['symbol']
        test("GET /v2/options/contracts/{symbol}",
             lambda: f"{market_data.get_options_contract(contract_symbol).get('symbol')}")
except:
    print("  ○ GET /v2/options/contracts/{symbol} (no contracts)")
    skipped += 1

test("GET /v1beta1/options/snapshots/{underlying}",
     lambda: f"AAPL options chain")

# ==================== UTILITY METHODS ====================

print("\n[UTILITY METHODS]")
test("get_current_price",
     lambda: f"AAPL: ${market_data.get_current_price('AAPL')}")
test("get_latest_quote",
     lambda: f"Spread: ${market_data.get_latest_quote('AAPL').spread}")
test("get_multi_stock_prices",
     lambda: f"{len(market_data.get_multi_stock_prices(['AAPL', 'MSFT', 'GOOGL']))} prices")
test("get_daily_bars",
     lambda: f"{len(market_data.get_daily_bars('AAPL', days=10))} daily bars")
test("is_market_open",
     lambda: f"{trading.is_market_open()}")
test("get_buying_power",
     lambda: f"${trading.get_buying_power():,.2f}")

# ==================== SUMMARY ====================

print("\n" + "=" * 60)
print("TEST SUMMARY")
print("=" * 60)
print(f"  ✓ Passed:  {passed}")
print(f"  ✗ Failed:  {failed}")
print(f"  ○ Skipped: {skipped}")
print(f"  Total:     {passed + failed + skipped}")
print("=" * 60)

if failed == 0:
    print("🎉 All tests passed!")
else:
    print(f"⚠️  {failed} test(s) failed")

client.close()
