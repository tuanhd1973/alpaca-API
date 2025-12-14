# Alpaca API Client - TypeScript

TypeScript/JavaScript client for Alpaca Trading and Market Data APIs.

## Installation

```bash
npm install
```

## Quick Start

```typescript
import 'dotenv/config';
import { AlpacaClient, TradingAPI, MarketDataAPI } from './src';

const client = new AlpacaClient({
  apiKey: process.env.ALPACA_API_KEY!,
  apiSecret: process.env.ALPACA_API_SECRET!,
  paper: true
});

const trading = new TradingAPI(client);
const marketData = new MarketDataAPI(client);

// Account
const account = await trading.getAccount();
console.log(`Buying Power: $${account.buyingPower}`);

// Order
const order = await trading.buy('AAPL', 10);

// Market Data
const price = await marketData.getCurrentPrice('AAPL');
```

## Build

```bash
npm run build
```

## Run Example

```bash
npx ts-node examples/basic.ts
```
