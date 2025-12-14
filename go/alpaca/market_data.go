package alpaca

import (
	"encoding/json"
	"fmt"
	"strings"
)

type MarketDataAPI struct {
	client *Client
}

func NewMarketDataAPI(client *Client) *MarketDataAPI {
	return &MarketDataAPI{client: client}
}

type BarsResponse struct {
	Bars          map[string][]Bar `json:"bars"`
	NextPageToken string           `json:"next_page_token"`
}

type TradesResponse struct {
	Trades        map[string][]Trade `json:"trades"`
	NextPageToken string             `json:"next_page_token"`
}

type SnapshotResponse struct {
	LatestTrade *Trade `json:"latestTrade"`
	LatestQuote *Quote `json:"latestQuote"`
	MinuteBar   *Bar   `json:"minuteBar"`
	DailyBar    *Bar   `json:"dailyBar"`
}

// Stock Bars
func (m *MarketDataAPI) GetStockBars(symbols []string, timeframe string, limit int) (*BarsResponse, error) {
	endpoint := fmt.Sprintf("/v2/stocks/bars?symbols=%s&timeframe=%s&limit=%d",
		strings.Join(symbols, ","), timeframe, limit)

	data, err := m.client.Get(endpoint, MarketData)
	if err != nil {
		return nil, err
	}

	var resp BarsResponse
	if err := json.Unmarshal(data, &resp); err != nil {
		return nil, err
	}
	return &resp, nil
}

// Stock Snapshot
func (m *MarketDataAPI) GetStockSnapshot(symbol string) (*SnapshotResponse, error) {
	endpoint := fmt.Sprintf("/v2/stocks/%s/snapshot", strings.ToUpper(symbol))

	data, err := m.client.Get(endpoint, MarketData)
	if err != nil {
		return nil, err
	}

	var resp SnapshotResponse
	if err := json.Unmarshal(data, &resp); err != nil {
		return nil, err
	}
	return &resp, nil
}

// Current Price
func (m *MarketDataAPI) GetCurrentPrice(symbol string) (float64, error) {
	snapshot, err := m.GetStockSnapshot(symbol)
	if err != nil {
		return 0, err
	}
	if snapshot.LatestTrade != nil {
		return snapshot.LatestTrade.Price, nil
	}
	return 0, fmt.Errorf("no trade data for %s", symbol)
}

// Crypto Bars
func (m *MarketDataAPI) GetCryptoBars(symbols []string, timeframe string, limit int) (*BarsResponse, error) {
	endpoint := fmt.Sprintf("/v1beta3/crypto/us/bars?symbols=%s&timeframe=%s&limit=%d",
		strings.Join(symbols, ","), timeframe, limit)

	data, err := m.client.Get(endpoint, MarketData)
	if err != nil {
		return nil, err
	}

	var resp BarsResponse
	if err := json.Unmarshal(data, &resp); err != nil {
		return nil, err
	}
	return &resp, nil
}
