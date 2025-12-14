"""
Quick connection test for Alpaca API
"""
import os
from dotenv import load_dotenv

# Load .env
load_dotenv()

API_KEY = os.environ.get("ALPACA_API_KEY")
API_SECRET = os.environ.get("ALPACA_API_SECRET")

if not API_KEY or not API_SECRET:
    print("❌ API credentials not found!")
    print("Create a .env file with:")
    print("  ALPACA_API_KEY=your_key")
    print("  ALPACA_API_SECRET=your_secret")
    exit(1)

print(f"API Key: {API_KEY[:8]}...{API_KEY[-4:]}")
print("Testing connection...")

try:
    from alpaca_client import AlpacaClient, TradingAPI, MarketDataAPI
    
    client = AlpacaClient(API_KEY, API_SECRET, paper=True)
    trading = TradingAPI(client)
    market_data = MarketDataAPI(client)
    
    # Test 1: Account
    print("\n[1] Account Info:")
    account = trading.get_account()
    print(f"  ✓ Account ID: {account.id}")
    print(f"  ✓ Status: {account.status}")
    print(f"  ✓ Buying Power: ${account.buying_power:,.2f}")
    print(f"  ✓ Cash: ${account.cash:,.2f}")
    
    # Test 2: Market Clock
    print("\n[2] Market Clock:")
    clock = trading.get_clock()
    print(f"  ✓ Market Open: {clock.is_open}")
    print(f"  ✓ Next Open: {clock.next_open}")
    
    # Test 3: Market Data
    print("\n[3] Market Data:")
    price = market_data.get_current_price("AAPL")
    print(f"  ✓ AAPL Price: ${price}")
    
    # Test 4: Positions
    print("\n[4] Positions:")
    positions = trading.get_positions()
    print(f"  ✓ Open Positions: {len(positions)}")
    
    # Test 5: Orders
    print("\n[5] Orders:")
    orders = trading.get_open_orders()
    print(f"  ✓ Open Orders: {len(orders)}")
    
    print("\n✅ All tests passed! API is working correctly.")
    
    client.close()

except Exception as e:
    print(f"\n❌ Error: {e}")
    import traceback
    traceback.print_exc()
