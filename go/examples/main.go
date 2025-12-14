package main

import (
	"fmt"
	"log"
	"os"

	"github.com/eneshenderson/alpaca-API/go/alpaca"
	"github.com/joho/godotenv"
)

func main() {
	// Load .env
	godotenv.Load()

	apiKey := os.Getenv("ALPACA_API_KEY")
	apiSecret := os.Getenv("ALPACA_API_SECRET")

	if apiKey == "" || apiSecret == "" {
		log.Fatal("ALPACA_API_KEY and ALPACA_API_SECRET required")
	}

	// Initialize client
	client := alpaca.NewClient(alpaca.ClientOptions{
		APIKey:    apiKey,
		APISecret: apiSecret,
		Paper:     true,
	})

	trading := alpaca.NewTradingAPI(client)
	marketData := alpaca.NewMarketDataAPI(client)

	// Account
	account, err := trading.GetAccount()
	if err != nil {
		log.Fatal(err)
	}
	fmt.Printf("Buying Power: $%s\n", account.BuyingPower)

	// Market status
	clock, err := trading.GetClock()
	if err != nil {
		log.Fatal(err)
	}
	fmt.Printf("Market Open: %v\n", clock.IsOpen)

	// Current price
	price, err := marketData.GetCurrentPrice("AAPL")
	if err != nil {
		log.Fatal(err)
	}
	fmt.Printf("AAPL: $%.2f\n", price)

	// Positions
	positions, err := trading.GetPositions()
	if err != nil {
		log.Fatal(err)
	}
	fmt.Printf("Positions: %d\n", len(positions))

	fmt.Println("Done!")
}
