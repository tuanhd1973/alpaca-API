package alpaca

import "time"

type Account struct {
	ID                string    `json:"id"`
	AccountNumber     string    `json:"account_number"`
	Status            string    `json:"status"`
	Currency          string    `json:"currency"`
	Cash              string    `json:"cash"`
	BuyingPower       string    `json:"buying_power"`
	PortfolioValue    string    `json:"portfolio_value"`
	Equity            string    `json:"equity"`
	LastEquity        string    `json:"last_equity"`
	DaytradeCount     int       `json:"daytrade_count"`
	PatternDayTrader  bool      `json:"pattern_day_trader"`
	TradingBlocked    bool      `json:"trading_blocked"`
	TransfersBlocked  bool      `json:"transfers_blocked"`
	AccountBlocked    bool      `json:"account_blocked"`
	CreatedAt         time.Time `json:"created_at"`
}

type Order struct {
	ID             string     `json:"id"`
	ClientOrderID  string     `json:"client_order_id"`
	CreatedAt      time.Time  `json:"created_at"`
	SubmittedAt    *time.Time `json:"submitted_at"`
	FilledAt       *time.Time `json:"filled_at"`
	AssetID        string     `json:"asset_id"`
	Symbol         string     `json:"symbol"`
	AssetClass     string     `json:"asset_class"`
	Qty            string     `json:"qty"`
	FilledQty      string     `json:"filled_qty"`
	FilledAvgPrice string     `json:"filled_avg_price"`
	Type           string     `json:"type"`
	Side           string     `json:"side"`
	TimeInForce    string     `json:"time_in_force"`
	LimitPrice     string     `json:"limit_price"`
	StopPrice      string     `json:"stop_price"`
	Status         string     `json:"status"`
	ExtendedHours  bool       `json:"extended_hours"`
}

type Position struct {
	AssetID        string `json:"asset_id"`
	Symbol         string `json:"symbol"`
	Exchange       string `json:"exchange"`
	AssetClass     string `json:"asset_class"`
	AvgEntryPrice  string `json:"avg_entry_price"`
	Qty            string `json:"qty"`
	Side           string `json:"side"`
	MarketValue    string `json:"market_value"`
	CostBasis      string `json:"cost_basis"`
	UnrealizedPL   string `json:"unrealized_pl"`
	UnrealizedPLPC string `json:"unrealized_plpc"`
	CurrentPrice   string `json:"current_price"`
	LastdayPrice   string `json:"lastday_price"`
	ChangeToday    string `json:"change_today"`
}

type Clock struct {
	Timestamp time.Time `json:"timestamp"`
	IsOpen    bool      `json:"is_open"`
	NextOpen  time.Time `json:"next_open"`
	NextClose time.Time `json:"next_close"`
}

type Bar struct {
	Timestamp  time.Time `json:"t"`
	Open       float64   `json:"o"`
	High       float64   `json:"h"`
	Low        float64   `json:"l"`
	Close      float64   `json:"c"`
	Volume     int64     `json:"v"`
	TradeCount int       `json:"n"`
	VWAP       float64   `json:"vw"`
}

type Trade struct {
	Timestamp  time.Time `json:"t"`
	Price      float64   `json:"p"`
	Size       int       `json:"s"`
	Exchange   string    `json:"x"`
	ID         int64     `json:"i"`
	Conditions []string  `json:"c"`
}

type Quote struct {
	Timestamp   time.Time `json:"t"`
	AskPrice    float64   `json:"ap"`
	AskSize     int       `json:"as"`
	BidPrice    float64   `json:"bp"`
	BidSize     int       `json:"bs"`
	AskExchange string    `json:"ax"`
	BidExchange string    `json:"bx"`
}

type OrderRequest struct {
	Symbol        string `json:"symbol"`
	Qty           string `json:"qty,omitempty"`
	Notional      string `json:"notional,omitempty"`
	Side          string `json:"side"`
	Type          string `json:"type"`
	TimeInForce   string `json:"time_in_force"`
	LimitPrice    string `json:"limit_price,omitempty"`
	StopPrice     string `json:"stop_price,omitempty"`
	ExtendedHours bool   `json:"extended_hours,omitempty"`
}
