# Alpaca Markets Java Client

Java client for Alpaca Trading and Market Data APIs.

## Requirements

- Java 11+
- Maven 3.6+

## Installation

### With Gradle
```bash
cd java
gradle build
```

### With Maven
```bash
cd java
mvn clean install
```

## Configuration

Create a `.env` file:

```env
ALPACA_API_KEY=your_api_key
ALPACA_API_SECRET=your_api_secret
ALPACA_PAPER=true
```

## Usage

```java
import com.alpaca.client.*;
import com.alpaca.client.models.*;

// Initialize client
AlpacaClient client = new AlpacaClient(apiKey, apiSecret, true);
TradingApi trading = new TradingApi(client);
MarketDataApi marketData = new MarketDataApi(client);

// Get account
Account account = trading.getAccount();
System.out.println("Buying Power: $" + account.getBuyingPower());

// Get current price
double price = marketData.getCurrentPrice("AAPL");
System.out.printf("AAPL: $%.2f%n", price);

// Submit order
Order order = trading.submitOrder(OrderRequest.market("AAPL", "1", "buy"));
```

## Run Example

### With Gradle
```bash
gradle run
```

### With Maven
```bash
mvn exec:java
```

## API Reference

### TradingApi
- `getAccount()` - Get account info
- `getClock()` - Get market clock
- `getPositions()` - Get all positions
- `getOrders()` - Get all orders
- `submitOrder(OrderRequest)` - Submit new order
- `cancelOrder(orderId)` - Cancel order
- `cancelAllOrders()` - Cancel all orders

### MarketDataApi
- `getCurrentPrice(symbol)` - Get current price
- `getLatestQuote(symbol)` - Get latest quote
- `getLatestTrade(symbol)` - Get latest trade
- `getSnapshot(symbol)` - Get market snapshot
