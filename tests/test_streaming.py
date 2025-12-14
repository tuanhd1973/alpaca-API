"""
Test Alpaca Streaming API
"""
import os
import asyncio
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.environ.get("ALPACA_API_KEY")
API_SECRET = os.environ.get("ALPACA_API_SECRET")

from alpaca_client.streaming import AlpacaStream, StreamType, StreamConfig

print("=" * 60)
print("ALPACA STREAMING TEST")
print("=" * 60)

# Track received messages
received = {"trades": 0, "quotes": 0, "bars": 0, "connected": False}

async def test_market_data_stream():
    """Test market data streaming (IEX)"""
    print("\n[1] MARKET DATA STREAM (IEX)")
    print("-" * 40)
    
    config = StreamConfig(
        auto_reconnect=False,
        ping_interval=30,
    )
    
    stream = AlpacaStream(
        api_key=API_KEY,
        api_secret=API_SECRET,
        stream_type=StreamType.IEX,
        config=config,
    )
    
    @stream.on_connect
    async def on_connect(data):
        received["connected"] = True
        print(f"  ✓ Connected to {data.get('url')}")
    
    @stream.on_trade
    async def on_trade(data):
        received["trades"] += 1
        symbol = data.get("S")
        price = data.get("p")
        size = data.get("s")
        print(f"  [TRADE] {symbol}: {size} @ ${price}")
    
    @stream.on_quote
    async def on_quote(data):
        received["quotes"] += 1
        symbol = data.get("S")
        bid = data.get("bp")
        ask = data.get("ap")
        print(f"  [QUOTE] {symbol}: Bid ${bid} / Ask ${ask}")
    
    @stream.on_bar
    async def on_bar(data):
        received["bars"] += 1
        symbol = data.get("S")
        close = data.get("c")
        print(f"  [BAR] {symbol}: Close ${close}")
    
    @stream.on_error
    async def on_error(data):
        print(f"  [ERROR] {data}")
    
    try:
        # Connect
        print("  Connecting...")
        connected = await stream.connect()
        
        if not connected:
            print("  ✗ Failed to connect")
            return False
        
        print("  ✓ Authenticated")
        
        # Subscribe
        print("  Subscribing to AAPL, MSFT...")
        result = await stream.subscribe(
            trades=["AAPL", "MSFT"],
            quotes=["AAPL"],
        )
        print(f"  ✓ Subscribed: {result}")
        
        # Listen for a few seconds
        print("  Listening for 10 seconds...")
        print("  (Market is closed on weekends, may not receive data)")
        
        async def listen_with_timeout():
            try:
                await asyncio.wait_for(stream.run(), timeout=10)
            except asyncio.TimeoutError:
                pass
        
        await listen_with_timeout()
        
        # Unsubscribe
        print("  Unsubscribing...")
        await stream.unsubscribe(trades=["AAPL", "MSFT"], quotes=["AAPL"])
        
        # Disconnect
        await stream.disconnect()
        print("  ✓ Disconnected")
        
        return True
        
    except Exception as e:
        print(f"  ✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_crypto_stream():
    """Test crypto streaming"""
    print("\n[2] CRYPTO STREAM")
    print("-" * 40)
    
    crypto_received = {"trades": 0, "bars": 0}
    
    stream = AlpacaStream(
        api_key=API_KEY,
        api_secret=API_SECRET,
        stream_type=StreamType.CRYPTO,
    )
    
    @stream.on_trade
    async def on_crypto_trade(data):
        crypto_received["trades"] += 1
        symbol = data.get("S")
        price = data.get("p")
        print(f"  [CRYPTO TRADE] {symbol}: ${price:,.2f}")
    
    @stream.on_bar
    async def on_crypto_bar(data):
        crypto_received["bars"] += 1
        symbol = data.get("S")
        close = data.get("c")
        print(f"  [CRYPTO BAR] {symbol}: ${close:,.2f}")
    
    try:
        print("  Connecting to crypto stream...")
        connected = await stream.connect()
        
        if not connected:
            print("  ✗ Failed to connect")
            return False
        
        print("  ✓ Connected and authenticated")
        
        # Subscribe to BTC
        print("  Subscribing to BTC/USD...")
        result = await stream.subscribe(trades=["BTC/USD"])
        print(f"  ✓ Subscribed")
        
        # Listen for 10 seconds
        print("  Listening for 10 seconds...")
        
        async def listen_with_timeout():
            try:
                await asyncio.wait_for(stream.run(), timeout=10)
            except asyncio.TimeoutError:
                pass
        
        await listen_with_timeout()
        
        await stream.disconnect()
        print(f"  ✓ Received {crypto_received['trades']} trades")
        
        return True
        
    except Exception as e:
        print(f"  ✗ Error: {e}")
        return False


async def main():
    # Test market data stream
    market_ok = await test_market_data_stream()
    
    # Test crypto stream
    crypto_ok = await test_crypto_stream()
    
    # Summary
    print("\n" + "=" * 60)
    print("STREAMING TEST SUMMARY")
    print("=" * 60)
    print(f"  Market Data Stream: {'✓ OK' if market_ok else '✗ FAILED'}")
    print(f"  Crypto Stream: {'✓ OK' if crypto_ok else '✗ FAILED'}")
    print(f"  Trades received: {received['trades']}")
    print(f"  Quotes received: {received['quotes']}")
    print("=" * 60)
    
    if received["trades"] == 0 and received["quotes"] == 0:
        print("Note: No market data received (market is closed on weekends)")
        print("Crypto trades should still come through 24/7")


if __name__ == "__main__":
    asyncio.run(main())
