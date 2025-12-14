package alpaca

import (
	"bytes"
	"encoding/json"
	"fmt"
	"io"
	"net/http"
	"time"
)

const (
	TradingLive  = "https://api.alpaca.markets"
	TradingPaper = "https://paper-api.alpaca.markets"
	MarketData   = "https://data.alpaca.markets"
)

type ClientOptions struct {
	APIKey    string
	APISecret string
	Paper     bool
	Timeout   time.Duration
}

type Client struct {
	apiKey    string
	apiSecret string
	baseURL   string
	client    *http.Client
}

func NewClient(opts ClientOptions) *Client {
	baseURL := TradingPaper
	if !opts.Paper {
		baseURL = TradingLive
	}

	timeout := opts.Timeout
	if timeout == 0 {
		timeout = 30 * time.Second
	}

	return &Client{
		apiKey:    opts.APIKey,
		apiSecret: opts.APISecret,
		baseURL:   baseURL,
		client:    &http.Client{Timeout: timeout},
	}
}

func (c *Client) request(method, endpoint string, body interface{}, baseURL string) ([]byte, error) {
	if baseURL == "" {
		baseURL = c.baseURL
	}

	var bodyReader io.Reader
	if body != nil {
		jsonBody, err := json.Marshal(body)
		if err != nil {
			return nil, err
		}
		bodyReader = bytes.NewReader(jsonBody)
	}

	req, err := http.NewRequest(method, baseURL+endpoint, bodyReader)
	if err != nil {
		return nil, err
	}

	req.Header.Set("APCA-API-KEY-ID", c.apiKey)
	req.Header.Set("APCA-API-SECRET-KEY", c.apiSecret)
	req.Header.Set("Content-Type", "application/json")

	resp, err := c.client.Do(req)
	if err != nil {
		return nil, err
	}
	defer resp.Body.Close()

	data, err := io.ReadAll(resp.Body)
	if err != nil {
		return nil, err
	}

	if resp.StatusCode >= 400 {
		return nil, fmt.Errorf("API error %d: %s", resp.StatusCode, string(data))
	}

	return data, nil
}

func (c *Client) Get(endpoint string, baseURL string) ([]byte, error) {
	return c.request("GET", endpoint, nil, baseURL)
}

func (c *Client) Post(endpoint string, body interface{}) ([]byte, error) {
	return c.request("POST", endpoint, body, "")
}

func (c *Client) Delete(endpoint string) ([]byte, error) {
	return c.request("DELETE", endpoint, nil, "")
}
