# Alpaca API Client

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://python.org)

Alpaca Markets Trading ve Market Data API'leri için kapsamlı Python client kütüphanesi.

## 🎯 Ne İşe Yarar?

Bu kütüphane ile Alpaca üzerinden programatik olarak trading yapabilirsiniz:

- **Trading**: Hisse senedi, crypto ve opsiyon alım/satım
- **Market Data**: Gerçek zamanlı ve geçmiş fiyat verileri
- **Streaming**: WebSocket ile canlı veri akışı
- **Paper Trading**: Gerçek para riski olmadan test

## 📊 Desteklenen Özellikler

| Özellik | Açıklama |
|---------|----------|
| **Trading API** | Account, Orders, Positions, Watchlists |
| **Market Data** | Stocks, Crypto, Options (Bars, Trades, Quotes) |
| **Streaming** | Real-time WebSocket (IEX, SIP, Crypto) |
| **Paper Trading** | Risk-free testing environment |

## 🚀 Hızlı Başlangıç

### Kurulum

```bash
git clone https://github.com/eneshenderson/alpaca-API.git
cd alpaca-API
pip install -r requirements.txt
```

### Credential Ayarları

```bash
cp .env.example .env
# .env dosyasını düzenle ve API key'lerini gir
```

`.env` dosyası:
```env
ALPACA_API_KEY=your_api_key_here
ALPACA_API_SECRET=your_api_secret_here
ALPACA_PAPER=true
```

> API key'lerinizi [Alpaca Dashboard](https://app.alpaca.markets)'dan alabilirsiniz.

### Temel Kullanım

```python
import os
from dotenv import load_dotenv
from alpaca_client import AlpacaClient, TradingAPI, MarketDataAPI

load_dotenv()

# Client oluştur
client = AlpacaClient(
    api_key=os.environ["ALPACA_API_KEY"],
    api_secret=os.environ["ALPACA_API_SECRET"],
    paper=True  # Paper trading
)

trading = TradingAPI(client)
market_data = MarketDataAPI(client)

# Hesap bilgisi
account = trading.get_account()
print(f"Buying Power: ${account.buying_power:,.2f}")

# Fiyat sorgula
price = market_data.get_current_price("AAPL")
print(f"AAPL: ${price}")

# Order ver
order = trading.buy("AAPL", qty=10)
print(f"Order: {order.id} - {order.status}")
```

### Streaming (Canlı Veri)

```python
import asyncio
from alpaca_client.streaming import AlpacaStream, StreamType

stream = AlpacaStream(API_KEY, API_SECRET, StreamType.IEX)

@stream.on_trade
async def handle_trade(data):
    print(f"{data['S']}: ${data['p']}")

async def main():
    async with stream:
        await stream.subscribe(trades=["AAPL", "MSFT"])
        await stream.run()

asyncio.run(main())
```


## 📚 API Metodları

### Trading API

| Metod | Açıklama |
|-------|----------|
| `get_account()` | Hesap bilgilerini getirir |
| `buy(symbol, qty)` | Market buy order |
| `sell(symbol, qty)` | Market sell order |
| `buy_limit(symbol, qty, price)` | Limit buy order |
| `bracket_order(...)` | Entry + TP + SL order |
| `get_orders()` | Tüm order'ları listeler |
| `cancel_order(id)` | Order iptal eder |
| `get_positions()` | Açık pozisyonları listeler |
| `close_position(symbol)` | Pozisyon kapatır |
| `get_clock()` | Market durumunu getirir |

### Market Data API

| Metod | Açıklama |
|-------|----------|
| `get_stock_bars(symbols, timeframe)` | Geçmiş OHLCV verileri |
| `get_stock_snapshot(symbol)` | Anlık fiyat verisi |
| `get_current_price(symbol)` | Güncel fiyat |
| `get_crypto_bars(symbols, timeframe)` | Crypto OHLCV verileri |
| `get_options_contracts(...)` | Opsiyon kontratları |

### Streaming API

| Metod | Açıklama |
|-------|----------|
| `subscribe(trades, quotes, bars)` | Veri akışına abone ol |
| `unsubscribe(...)` | Aboneliği iptal et |
| `on_trade` | Trade event handler |
| `on_quote` | Quote event handler |
| `on_bar` | Bar event handler |

## 🏗️ Proje Yapısı

```
alpaca-API/
├── alpaca_client/           # Ana modül
│   ├── __init__.py          # Package exports
│   ├── client.py            # HTTP client (retry, rate limit)
│   ├── trading.py           # Trading API
│   ├── market_data.py       # Market Data API
│   ├── broker.py            # Broker API (B2B)
│   ├── streaming.py         # WebSocket streaming
│   ├── models.py            # Dataclass models
│   └── exceptions.py        # Custom exceptions
├── tests/                   # Test dosyaları
├── .env.example             # Credential template
├── requirements.txt         # Dependencies
├── example.py               # Kullanım örnekleri
└── example_streaming.py     # Streaming örnekleri
```

## ⚙️ Yapılandırma

### Client Parametreleri

| Parametre | Varsayılan | Açıklama |
|-----------|------------|----------|
| `paper` | `True` | Paper trading modu |
| `timeout` | `30` | Request timeout (saniye) |
| `max_retries` | `3` | Retry sayısı |

### Streaming Parametreleri

| Parametre | Varsayılan | Açıklama |
|-----------|------------|----------|
| `auto_reconnect` | `True` | Otomatik yeniden bağlanma |
| `reconnect_attempts` | `10` | Max reconnect denemesi |

## 🛡️ Error Handling

```python
from alpaca_client import (
    AlpacaError,
    AuthenticationError,
    RateLimitError,
    NotFoundError,
    ValidationError
)

try:
    order = trading.buy("AAPL", qty=1000000)
except ValidationError as e:
    print(f"Geçersiz order: {e}")
except RateLimitError as e:
    print(f"Rate limit, {e.retry_after}s bekle")
except AlpacaError as e:
    print(f"API hatası: {e}")
```

## 🔗 Linkler

- [Alpaca Documentation](https://docs.alpaca.markets)
- [Alpaca Dashboard](https://app.alpaca.markets)
- [API Status](https://status.alpaca.markets)

## 🤝 Katkıda Bulunma

1. Fork edin
2. Feature branch oluşturun (`git checkout -b feature/amazing-feature`)
3. Commit edin (`git commit -m 'Add amazing feature'`)
4. Push edin (`git push origin feature/amazing-feature`)
5. Pull Request açın

## 📄 Lisans

Bu proje MIT lisansı altında lisanslanmıştır. Detaylar için [LICENSE](LICENSE) dosyasına bakın.

## 👤 Geliştirici

**Enes Hikmet Kayım**
- GitHub: [@eneshenderson](https://github.com/eneshenderson)

## ⚠️ Sorumluluk Reddi

Bu kütüphane resmi Alpaca API'si değildir. Yatırım kararlarınızda bu verileri kullanmadan önce kendi araştırmanızı yapın. Paper trading ile test etmeniz önerilir.
