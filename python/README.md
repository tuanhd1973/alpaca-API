# Alpaca API Client - Python

Python client for Alpaca Trading and Market Data APIs.

## Installation

```bash
pip install -r requirements.txt
```

## Quick Start

```python
import os
from dotenv import load_dotenv
from alpaca_client import AlpacaClient, TradingAPI, MarketDataAPI

load_dotenv()

client = AlpacaClient(
    api_key=os.environ["ALPACA_API_KEY"],
    api_secret=os.environ["ALPACA_API_SECRET"],
    paper=True
)

trading = TradingAPI(client)
market_data = MarketDataAPI(client)

# Account
account = trading.get_account()
print(f"Buying Power: ${account.buying_power:,.2f}")

# Order
order = trading.buy("AAPL", qty=10)

# Market Data
price = market_data.get_current_price("AAPL")
```

## Streaming

```python
import asyncio
from alpaca_client.streaming import AlpacaStream, StreamType

stream = AlpacaStream(API_KEY, API_SECRET, StreamType.IEX)

@stream.on_trade
async def handle_trade(data):
    print(f"{data['S']}: ${data['p']}")

async def main():
    async with stream:
        await stream.subscribe(trades=["AAPL"])
        await stream.run()

asyncio.run(main())
```

## Tests

```bash
python -m pytest tests/
```
