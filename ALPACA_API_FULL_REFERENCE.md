
# 🦙 Alpaca Markets API – Full Endpoint Reference

> Official Docs: https://docs.alpaca.markets  
> Scope: Trading API + Market Data + Crypto + Options + Broker + Streaming  
> Format: Markdown (single file)

---

## 🔐 Authentication

```http
APCA-API-KEY-ID: YOUR_API_KEY
APCA-API-SECRET-KEY: YOUR_API_SECRET
```

---

## 🌍 Base URLs

```text
Trading (Live)        https://api.alpaca.markets
Trading (Paper)       https://paper-api.alpaca.markets
Market Data           https://data.alpaca.markets
Broker (Sandbox)      https://broker-api.sandbox.alpaca.markets
Broker (Production)   https://broker-api.alpaca.markets
```

---

# 1️⃣ TRADING API (v2)

## Account

```http
GET    /v2/account
GET    /v2/account/configurations
PATCH  /v2/account/configurations
GET    /v2/account/activities
GET    /v2/account/activities/{activity_type}
GET    /v2/account/portfolio/history
```

## Assets

```http
GET /v2/assets
GET /v2/assets/{symbol_or_asset_id}
```

## Orders

```http
POST   /v2/orders
GET    /v2/orders
GET    /v2/orders/{order_id}
PATCH  /v2/orders/{order_id}
DELETE /v2/orders/{order_id}
DELETE /v2/orders
```

## Positions

```http
GET    /v2/positions
GET    /v2/positions/{symbol_or_asset_id}
DELETE /v2/positions
DELETE /v2/positions/{symbol_or_asset_id}
```

## Watchlists

```http
POST   /v2/watchlists
GET    /v2/watchlists
GET    /v2/watchlists/{watchlist_id}
GET    /v2/watchlists/{watchlist_name}
PUT    /v2/watchlists/{watchlist_id}
POST   /v2/watchlists/{watchlist_id}
DELETE /v2/watchlists/{watchlist_id}
DELETE /v2/watchlists/{watchlist_id}/{symbol}
```

## System

```http
GET /v2/clock
GET /v2/calendar
```

---

# 2️⃣ MARKET DATA API

## Stocks

```http
GET /v2/stocks/bars
GET /v2/stocks/trades
GET /v2/stocks/quotes
GET /v2/stocks/snapshots
GET /v2/stocks/snapshots/{symbol}
```

## Stock Meta

```http
GET /v2/stocks/meta/exchanges
GET /v2/stocks/meta/conditions/trades
GET /v2/stocks/meta/conditions/quotes
```

## Crypto

```http
GET /v2/crypto/bars
GET /v2/crypto/trades
GET /v2/crypto/quotes
GET /v2/crypto/snapshots
GET /v2/crypto/snapshots/{symbol}
GET /v2/crypto/meta/symbols
```

---

# 3️⃣ OPTIONS API (BETA)

```http
GET /v2/options/contracts
GET /v2/options/contracts/{symbol_or_id}
GET /v1beta1/options/bars
GET /v1beta1/options/trades
GET /v1beta1/options/quotes
GET /v1beta1/options/snapshots/{underlying_symbol}
```

---

# 4️⃣ BROKER API

## Accounts

```http
POST   /v1/accounts
GET    /v1/accounts
GET    /v1/accounts/{account_id}
PATCH  /v1/accounts/{account_id}
```

## Documents & KYC

```http
POST /v1/accounts/{account_id}/documents
GET  /v1/accounts/{account_id}/documents
```

## Banks & Transfers

```http
POST /v1/accounts/{account_id}/recipient_banks
GET  /v1/accounts/{account_id}/recipient_banks
POST /v1/accounts/{account_id}/transfers
GET  /v1/accounts/{account_id}/transfers
```

## Broker Trading

```http
POST /v1/trading/accounts/{account_id}/orders
GET  /v1/trading/accounts/{account_id}/orders
GET  /v1/trading/accounts/{account_id}/positions
```

---

# 5️⃣ STREAMING

```text
wss://stream.data.alpaca.markets/v2/iex
wss://stream.data.alpaca.markets/v2/sip
wss://paper-api.alpaca.markets/stream
```

---

# 6️⃣ DEPRECATED

```http
/v1/account
/v1/orders
/v1/positions
```

---

## ✅ Coverage

✔ Trading API  
✔ Market Data (Stocks + Crypto)  
✔ Options (Beta)  
✔ Broker API  
✔ Streaming  

