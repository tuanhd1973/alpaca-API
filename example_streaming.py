"""
Alpaca Streaming API - Real-time Data Examples

Requires: pip install websockets python-dotenv
"""
import os
import asyncio
import logging
from datetime import datetime

from dotenv import load_dotenv

from alpaca_client.streaming import (
    AlpacaStream,
    TradingStream,
    StreamType,
    StreamConfig,
)

# Load .env file
load_dotenv()

API_KEY = os.environ.get("ALPACA_API_KEY")
API_SECRET = os.environ.get("ALPACA_API_SECRET")

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)


# ==================== MARKET DATA STREAMING ====================

async def market_data_example():
    """Stream real-time market data (trades, quotes, bars)."""
    
    # Configure stream
    config = StreamConfig(
        auto_reconnect=True,
        reconnect_attempts=5,
        ping_interval=30,
    )
    
    stream = AlpacaStream(
        api_key=API_KEY,
        api_secret=API_SECRET,
        stream_type=StreamType.IEX,  # Free tier
        config=config,
    )
    
    # Register handlers using decorators
    @stream.on_trade
    async def handle_trade(data):
        """Handle trade events."""
        symbol = data.get("S")
        price = data.get("p")
        size = data.get("s")
        timestamp = data.get("t")
        print(f"[TRADE] {symbol}: {size} @ ${price} ({timestamp})")
    
    @stream.on_quote
    async def handle_quote(data):
        """Handle quote events."""
        symbol = data.get("S")
        bid = data.get("bp")
        ask = data.get("ap")
        bid_size = data.get("bs")
        ask_size = data.get("as")
        spread = ask - bid if bid and ask else 0
        print(f"[QUOTE] {symbol}: Bid ${bid} x {bid_size} | Ask ${ask} x {ask_size} | Spread ${spread:.4f}")
    
    @stream.on_bar
    async def handle_bar(data):
        """Handle minute bar events."""
        symbol = data.get("S")
        o, h, l, c = data.get("o"), data.get("h"), data.get("l"), data.get("c")
        volume = data.get("v")
        print(f"[BAR] {symbol}: O={o} H={h} L={l} C={c} V={volume}")
    
    @stream.on_connect
    async def on_connect(data):
        print(f"✓ Connected to {data.get('url')}")
    
    @stream.on_disconnect
    async def on_disconnect(data):
        print("✗ Disconnected")
    
    @stream.on_error
    async def on_error(data):
        print(f"⚠ Error: {data}")
    
    # Run stream
    async with stream:
        # Subscribe to data
        await stream.subscribe(
            trades=["AAPL", "MSFT", "GOOGL"],
            quotes=["AAPL"],
            bars=["AAPL", "MSFT"],
        )
        
        print("Streaming... Press Ctrl+C to stop")
        
        try:
            await stream.run()
        except KeyboardInterrupt:
            print("\nStopping...")


# ==================== TRADING UPDATES STREAMING ====================

async def trading_updates_example():
    """Stream real-time order/trade updates."""
    
    stream = TradingStream(
        api_key=API_KEY,
        api_secret=API_SECRET,
        paper=True,  # Paper trading
    )
    
    @stream.on_trade_update
    async def handle_trade_update(data):
        """Handle order fill/update events."""
        event = data.get("event")
        order = data.get("order", {})
        
        symbol = order.get("symbol")
        side = order.get("side")
        qty = order.get("qty")
        filled_qty = order.get("filled_qty")
        status = order.get("status")
        
        print(f"[{event.upper()}] {symbol}: {side} {qty} (filled: {filled_qty}) - {status}")
        
        if event == "fill":
            filled_price = order.get("filled_avg_price")
            print(f"  → Filled at ${filled_price}")
        elif event == "partial_fill":
            print(f"  → Partial fill: {filled_qty}/{qty}")
        elif event == "canceled":
            print(f"  → Order canceled")
        elif event == "rejected":
            print(f"  → Order rejected")
    
    async with stream:
        await stream.subscribe_trade_updates()
        
        print("Listening for trade updates... Press Ctrl+C to stop")
        print("Place orders in another terminal to see updates")
        
        try:
            await stream.run()
        except KeyboardInterrupt:
            print("\nStopping...")


# ==================== CRYPTO STREAMING ====================

async def crypto_streaming_example():
    """Stream real-time crypto data."""
    
    stream = AlpacaStream(
        api_key=API_KEY,
        api_secret=API_SECRET,
        stream_type=StreamType.CRYPTO,
    )
    
    @stream.on_trade
    async def handle_crypto_trade(data):
        symbol = data.get("S")
        price = data.get("p")
        size = data.get("s")
        print(f"[CRYPTO] {symbol}: {size} @ ${price:,.2f}")
    
    @stream.on_bar
    async def handle_crypto_bar(data):
        symbol = data.get("S")
        close = data.get("c")
        volume = data.get("v")
        print(f"[CRYPTO BAR] {symbol}: ${close:,.2f} Vol: {volume}")
    
    async with stream:
        await stream.subscribe(
            trades=["BTC/USD", "ETH/USD"],
            bars=["BTC/USD"],
        )
        
        print("Streaming crypto... Press Ctrl+C to stop")
        
        try:
            await stream.run()
        except KeyboardInterrupt:
            print("\nStopping...")


# ==================== ADVANCED: MULTIPLE STREAMS ====================

async def multi_stream_example():
    """Run multiple streams concurrently."""
    
    # Market data stream
    market_stream = AlpacaStream(
        api_key=API_KEY,
        api_secret=API_SECRET,
        stream_type=StreamType.IEX,
    )
    
    # Trading updates stream
    trading_stream = TradingStream(
        api_key=API_KEY,
        api_secret=API_SECRET,
        paper=True,
    )
    
    @market_stream.on_trade
    async def on_market_trade(data):
        print(f"[MARKET] {data.get('S')}: ${data.get('p')}")
    
    @trading_stream.on_trade_update
    async def on_order_update(data):
        print(f"[ORDER] {data.get('event')}: {data.get('order', {}).get('symbol')}")
    
    async def run_market_stream():
        async with market_stream:
            await market_stream.subscribe(trades=["AAPL", "MSFT"])
            await market_stream.run()
    
    async def run_trading_stream():
        async with trading_stream:
            await trading_stream.subscribe_trade_updates()
            await trading_stream.run()
    
    # Run both streams concurrently
    await asyncio.gather(
        run_market_stream(),
        run_trading_stream(),
    )


# ==================== MAIN ====================

if __name__ == "__main__":
    print("Choose example:")
    print("1. Market Data Streaming")
    print("2. Trading Updates Streaming")
    print("3. Crypto Streaming")
    print("4. Multi-Stream")
    
    choice = input("Enter choice (1-4): ").strip()
    
    if choice == "1":
        asyncio.run(market_data_example())
    elif choice == "2":
        asyncio.run(trading_updates_example())
    elif choice == "3":
        asyncio.run(crypto_streaming_example())
    elif choice == "4":
        asyncio.run(multi_stream_example())
    else:
        print("Invalid choice")
