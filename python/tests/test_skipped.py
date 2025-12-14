"""
Test previously skipped endpoints:
1. GET /v2/positions/{symbol} - needs open position
2. PATCH /v2/orders/{id} - needs pending order (market open)
3. GET /v2/options/contracts - needs valid query
"""
import os
import time
from datetime import datetime, timedelta, date
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.environ.get("ALPACA_API_KEY")
API_SECRET = os.environ.get("ALPACA_API_SECRET")

from alpaca_client import (
    AlpacaClient, TradingAPI, MarketDataAPI,
    AlpacaError, NotFoundError
)

client = AlpacaClient(API_KEY, API_SECRET, paper=True)
trading = TradingAPI(client)
market_data = MarketDataAPI(client)

print("=" * 60)
print("TESTING PREVIOUSLY SKIPPED ENDPOINTS")
print("=" * 60)

# ==================== 1. POSITIONS ====================
print("\n[1] POSITION TEST")
print("-" * 40)

# Check if we have any position
positions = trading.get_positions()
if positions:
    symbol = positions[0].symbol
    print(f"Found existing position: {symbol}")
    pos = trading.get_position(symbol)
    print(f"  ✓ GET /v2/positions/{symbol}")
    print(f"    → {pos.qty} shares @ ${pos.avg_entry_price}")
else:
    print("No positions. Creating one...")
    
    # Buy 1 share of a cheap stock (market order won't fill on weekend)
    # Use limit order at current price
    try:
        snapshot = market_data.get_stock_snapshot("AAPL")
        current_price = float(snapshot.latest_trade.price)
        
        # Place market order (will queue for market open)
        order = trading.buy("AAPL", qty=1)
        print(f"  ✓ Created buy order: {order.id[:8]}...")
        print(f"    → Status: {order.status}")
        
        # Wait a bit
        time.sleep(2)
        
        # Check order status
        order = trading.get_order(order.id)
        print(f"    → Updated status: {order.status}")
        
        if order.status == "filled":
            pos = trading.get_position("AAPL")
            print(f"  ✓ GET /v2/positions/AAPL")
            print(f"    → {pos.qty} shares @ ${pos.avg_entry_price}")
        else:
            print(f"  ○ Order not filled yet (market closed)")
            print(f"    → Will fill when market opens")
            
    except Exception as e:
        print(f"  ✗ Error: {e}")

# ==================== 2. ORDER UPDATE ====================
print("\n[2] ORDER UPDATE TEST")
print("-" * 40)

try:
    # Create a limit order far from market price (won't fill)
    order = trading.buy_limit("MSFT", qty=1, limit_price=100.00)
    print(f"  ✓ Created limit order: {order.id[:8]}...")
    print(f"    → MSFT @ $100 (far below market)")
    
    time.sleep(2)
    
    # Check status
    order = trading.get_order(order.id)
    print(f"    → Status: {order.status}")
    
    # Try to update
    if order.status in ["new", "pending_new"]:
        updated = trading.update_order(order.id, limit_price=105.00)
        print(f"  ✓ PATCH /v2/orders/{order.id[:8]}...")
        print(f"    → New price: ${updated.limit_price}")
        order_id = updated.id
    else:
        print(f"  ○ Cannot update order in '{order.status}' status")
        order_id = order.id
    
    # Cancel
    trading.cancel_order(order_id)
    print(f"  ✓ Canceled order")
    
except Exception as e:
    print(f"  ✗ Error: {e}")

# ==================== 3. OPTIONS CONTRACTS ====================
print("\n[3] OPTIONS CONTRACTS TEST")
print("-" * 40)

try:
    # Get options expiring in next 30 days
    today = date.today()
    next_month = today + timedelta(days=30)
    
    contracts = market_data.get_options_contracts(
        underlying_symbols=["AAPL"],
        expiration_date_gte=today.isoformat(),
        expiration_date_lte=next_month.isoformat(),
        type="call",
        strike_price_gte=250,
        strike_price_lte=300,
        limit=5,
    )
    
    options = contracts.get("option_contracts", [])
    print(f"  ✓ GET /v2/options/contracts")
    print(f"    → Found {len(options)} AAPL call options")
    
    if options:
        for opt in options[:3]:
            print(f"    → {opt['symbol']}: Strike ${opt['strike_price']} Exp {opt['expiration_date']}")
        
        # Get specific contract
        contract_symbol = options[0]["symbol"]
        contract = market_data.get_options_contract(contract_symbol)
        print(f"  ✓ GET /v2/options/contracts/{contract_symbol[:20]}...")
        print(f"    → Status: {contract.get('status')}")
    else:
        print("    → No options found in date range")
        
except Exception as e:
    print(f"  ✗ Error: {e}")

# ==================== 4. CLOSE POSITION (if created) ====================
print("\n[4] CLEANUP")
print("-" * 40)

try:
    positions = trading.get_positions()
    if positions:
        for pos in positions:
            print(f"  Closing {pos.symbol}...")
            trading.close_position(pos.symbol)
            print(f"  ✓ Closed {pos.symbol}")
    else:
        print("  No positions to close")
        
    # Cancel any open orders
    open_orders = trading.get_open_orders()
    if open_orders:
        trading.cancel_all_orders()
        print(f"  ✓ Canceled {len(open_orders)} open orders")
    else:
        print("  No open orders")
        
except Exception as e:
    print(f"  ✗ Error: {e}")

print("\n" + "=" * 60)
print("DONE")
print("=" * 60)

client.close()
