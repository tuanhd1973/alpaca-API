package alpaca

import (
	"encoding/json"
	"fmt"
	"strings"
)

type TradingAPI struct {
	client *Client
}

func NewTradingAPI(client *Client) *TradingAPI {
	return &TradingAPI{client: client}
}

// Account
func (t *TradingAPI) GetAccount() (*Account, error) {
	data, err := t.client.Get("/v2/account", "")
	if err != nil {
		return nil, err
	}

	var account Account
	if err := json.Unmarshal(data, &account); err != nil {
		return nil, err
	}
	return &account, nil
}

// Orders
func (t *TradingAPI) CreateOrder(req OrderRequest) (*Order, error) {
	req.Symbol = strings.ToUpper(req.Symbol)
	if req.Type == "" {
		req.Type = "market"
	}
	if req.TimeInForce == "" {
		req.TimeInForce = "day"
	}

	data, err := t.client.Post("/v2/orders", req)
	if err != nil {
		return nil, err
	}

	var order Order
	if err := json.Unmarshal(data, &order); err != nil {
		return nil, err
	}
	return &order, nil
}

func (t *TradingAPI) Buy(symbol string, qty int) (*Order, error) {
	return t.CreateOrder(OrderRequest{
		Symbol: symbol,
		Qty:    fmt.Sprintf("%d", qty),
		Side:   "buy",
		Type:   "market",
	})
}

func (t *TradingAPI) Sell(symbol string, qty int) (*Order, error) {
	return t.CreateOrder(OrderRequest{
		Symbol: symbol,
		Qty:    fmt.Sprintf("%d", qty),
		Side:   "sell",
		Type:   "market",
	})
}

func (t *TradingAPI) BuyLimit(symbol string, qty int, limitPrice float64) (*Order, error) {
	return t.CreateOrder(OrderRequest{
		Symbol:      symbol,
		Qty:         fmt.Sprintf("%d", qty),
		Side:        "buy",
		Type:        "limit",
		TimeInForce: "gtc",
		LimitPrice:  fmt.Sprintf("%.2f", limitPrice),
	})
}

func (t *TradingAPI) GetOrders() ([]Order, error) {
	data, err := t.client.Get("/v2/orders", "")
	if err != nil {
		return nil, err
	}

	var orders []Order
	if err := json.Unmarshal(data, &orders); err != nil {
		return nil, err
	}
	return orders, nil
}

func (t *TradingAPI) GetOrder(orderID string) (*Order, error) {
	data, err := t.client.Get("/v2/orders/"+orderID, "")
	if err != nil {
		return nil, err
	}

	var order Order
	if err := json.Unmarshal(data, &order); err != nil {
		return nil, err
	}
	return &order, nil
}

func (t *TradingAPI) CancelOrder(orderID string) error {
	_, err := t.client.Delete("/v2/orders/" + orderID)
	return err
}

// Positions
func (t *TradingAPI) GetPositions() ([]Position, error) {
	data, err := t.client.Get("/v2/positions", "")
	if err != nil {
		return nil, err
	}

	var positions []Position
	if err := json.Unmarshal(data, &positions); err != nil {
		return nil, err
	}
	return positions, nil
}

func (t *TradingAPI) GetPosition(symbol string) (*Position, error) {
	data, err := t.client.Get("/v2/positions/"+strings.ToUpper(symbol), "")
	if err != nil {
		return nil, err
	}

	var position Position
	if err := json.Unmarshal(data, &position); err != nil {
		return nil, err
	}
	return &position, nil
}

// Clock
func (t *TradingAPI) GetClock() (*Clock, error) {
	data, err := t.client.Get("/v2/clock", "")
	if err != nil {
		return nil, err
	}

	var clock Clock
	if err := json.Unmarshal(data, &clock); err != nil {
		return nil, err
	}
	return &clock, nil
}

func (t *TradingAPI) IsMarketOpen() (bool, error) {
	clock, err := t.GetClock()
	if err != nil {
		return false, err
	}
	return clock.IsOpen, nil
}
