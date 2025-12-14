# Alpaca API Client - Go

Go client for Alpaca Trading and Market Data APIs.

## Installation

```bash
go mod download
```

## Quick Start

```go
package main

import (
    "fmt"
    "os"
    "github.com/eneshenderson/alpaca-API/go/alpaca"
    "github.com/joho/godotenv"
)

func main() {
    godotenv.Load()

    client := alpaca.NewClient(alpaca.ClientOptions{
        APIKey:    os.Getenv("ALPACA_API_KEY"),
        APISecret: os.Getenv("ALPACA_API_SECRET"),
        Paper:     true,
    })

    trading := alpaca.NewTradingAPI(client)
    marketData := alpaca.NewMarketDataAPI(client)

    // Account
    account, _ := trading.GetAccount()
    fmt.Printf("Buying Power: $%s\n", account.BuyingPower)

    // Order
    order, _ := trading.Buy("AAPL", 10)

    // Market Data
    price, _ := marketData.GetCurrentPrice("AAPL")
    fmt.Printf("AAPL: $%.2f\n", price)
}
```

## Run Example

```bash
go run examples/main.go
```
