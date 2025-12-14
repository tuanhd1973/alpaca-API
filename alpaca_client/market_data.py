"""
Alpaca Market Data API (v2) - Full Implementation
"""
from typing import Optional, Dict, List, Any, Union, Iterator
from datetime import datetime, date
from decimal import Decimal

from .client import AlpacaClient
from .models import Bar, Trade, Quote, Snapshot


class MarketDataAPI:
    """
    Market Data API for stocks, crypto, and options.
    
    Supports both single requests and pagination for large datasets.
    """
    
    def __init__(self, client: AlpacaClient):
        self.client = client
        self.base_url = AlpacaClient.MARKET_DATA
    
    def _request(self, method: str, endpoint: str, **kwargs) -> Any:
        return self.client._request(method, endpoint, base_url=self.base_url, **kwargs)
    
    def _parse_datetime(self, dt: Union[datetime, date, str, None]) -> Optional[str]:
        """Convert datetime to RFC3339 string."""
        if dt is None:
            return None
        if isinstance(dt, str):
            return dt
        if isinstance(dt, datetime):
            # RFC3339 format with timezone
            if dt.tzinfo is None:
                return dt.strftime("%Y-%m-%dT%H:%M:%SZ")
            return dt.isoformat()
        if isinstance(dt, date):
            return dt.strftime("%Y-%m-%d")
        return str(dt)
    
    # ==================== STOCKS - BARS ====================
    
    def get_stock_bars(
        self,
        symbols: Union[str, List[str]],
        timeframe: str = "1Day",
        start: Optional[Union[datetime, date, str]] = None,
        end: Optional[Union[datetime, date, str]] = None,
        limit: Optional[int] = None,
        adjustment: str = "raw",
        feed: str = "iex",
        sort: str = "asc",
        page_token: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Get historical bars (OHLCV) for stocks.
        
        Args:
            symbols: Single symbol or list of symbols
            timeframe: Bar timeframe - '1Min', '5Min', '15Min', '30Min', 
                      '1Hour', '2Hour', '4Hour', '1Day', '1Week', '1Month'
            start: Start time (RFC3339 or date)
            end: End time
            limit: Max bars per symbol (default 1000, max 10000)
            adjustment: 'raw', 'split', 'dividend', 'all'
            feed: 'iex' (free) or 'sip' (paid)
            sort: 'asc' or 'desc'
            page_token: Pagination token
        
        Returns:
            Dict with 'bars' (symbol -> list of bars) and 'next_page_token'
        """
        if isinstance(symbols, str):
            symbols = [symbols]
        
        params = {
            "symbols": ",".join(s.upper() for s in symbols),
            "timeframe": timeframe,
            "adjustment": adjustment,
            "feed": feed,
            "sort": sort,
        }
        
        if start:
            params["start"] = self._parse_datetime(start)
        if end:
            params["end"] = self._parse_datetime(end)
        if limit:
            params["limit"] = min(limit, 10000)
        if page_token:
            params["page_token"] = page_token
        
        return self._request("GET", "/v2/stocks/bars", params=params)

    def get_stock_bars_iter(
        self,
        symbols: Union[str, List[str]],
        timeframe: str = "1Day",
        start: Optional[Union[datetime, date, str]] = None,
        end: Optional[Union[datetime, date, str]] = None,
        **kwargs
    ) -> Iterator[Dict[str, List[Bar]]]:
        """
        Iterate through all bars with automatic pagination.
        
        Yields:
            Dict mapping symbol to list of Bar objects for each page
        """
        page_token = None
        
        while True:
            response = self.get_stock_bars(
                symbols=symbols,
                timeframe=timeframe,
                start=start,
                end=end,
                page_token=page_token,
                **kwargs
            )
            
            bars_data = response.get("bars", {})
            if bars_data:
                result = {}
                for symbol, bars in bars_data.items():
                    result[symbol] = [Bar.from_dict(b) for b in bars]
                yield result
            
            page_token = response.get("next_page_token")
            if not page_token:
                break
    
    def get_all_stock_bars(
        self,
        symbols: Union[str, List[str]],
        timeframe: str = "1Day",
        start: Optional[Union[datetime, date, str]] = None,
        end: Optional[Union[datetime, date, str]] = None,
        **kwargs
    ) -> Dict[str, List[Bar]]:
        """
        Get all bars for symbols (handles pagination automatically).
        
        Returns:
            Dict mapping symbol to complete list of Bar objects
        """
        all_bars = {}
        
        for page in self.get_stock_bars_iter(symbols, timeframe, start, end, **kwargs):
            for symbol, bars in page.items():
                if symbol not in all_bars:
                    all_bars[symbol] = []
                all_bars[symbol].extend(bars)
        
        return all_bars
    
    # ==================== STOCKS - TRADES ====================
    
    def get_stock_trades(
        self,
        symbols: Union[str, List[str]],
        start: Optional[Union[datetime, date, str]] = None,
        end: Optional[Union[datetime, date, str]] = None,
        limit: Optional[int] = None,
        feed: str = "iex",
        sort: str = "asc",
        page_token: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Get historical trades for stocks.
        
        Args:
            symbols: Single symbol or list of symbols
            start: Start time
            end: End time
            limit: Max trades per symbol
            feed: 'iex' or 'sip'
            sort: 'asc' or 'desc'
            page_token: Pagination token
        
        Returns:
            Dict with 'trades' and 'next_page_token'
        """
        if isinstance(symbols, str):
            symbols = [symbols]
        
        params = {
            "symbols": ",".join(s.upper() for s in symbols),
            "feed": feed,
            "sort": sort,
        }
        
        if start:
            params["start"] = self._parse_datetime(start)
        if end:
            params["end"] = self._parse_datetime(end)
        if limit:
            params["limit"] = limit
        if page_token:
            params["page_token"] = page_token
        
        return self._request("GET", "/v2/stocks/trades", params=params)
    
    # ==================== STOCKS - QUOTES ====================
    
    def get_stock_quotes(
        self,
        symbols: Union[str, List[str]],
        start: Optional[Union[datetime, date, str]] = None,
        end: Optional[Union[datetime, date, str]] = None,
        limit: Optional[int] = None,
        feed: str = "iex",
        sort: str = "asc",
        page_token: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Get historical quotes (NBBO) for stocks.
        
        Args:
            symbols: Single symbol or list of symbols
            start: Start time
            end: End time
            limit: Max quotes per symbol
            feed: 'iex' or 'sip'
            sort: 'asc' or 'desc'
            page_token: Pagination token
        
        Returns:
            Dict with 'quotes' and 'next_page_token'
        """
        if isinstance(symbols, str):
            symbols = [symbols]
        
        params = {
            "symbols": ",".join(s.upper() for s in symbols),
            "feed": feed,
            "sort": sort,
        }
        
        if start:
            params["start"] = self._parse_datetime(start)
        if end:
            params["end"] = self._parse_datetime(end)
        if limit:
            params["limit"] = limit
        if page_token:
            params["page_token"] = page_token
        
        return self._request("GET", "/v2/stocks/quotes", params=params)

    # ==================== STOCKS - SNAPSHOTS ====================
    
    def get_stock_snapshots(
        self,
        symbols: Union[str, List[str]],
        feed: str = "iex",
    ) -> Dict[str, Snapshot]:
        """
        Get latest snapshots for multiple stocks.
        
        Args:
            symbols: Single symbol or list of symbols
            feed: 'iex' or 'sip'
        
        Returns:
            Dict mapping symbol to Snapshot object
        """
        if isinstance(symbols, str):
            symbols = [symbols]
        
        params = {
            "symbols": ",".join(s.upper() for s in symbols),
            "feed": feed,
        }
        
        data = self._request("GET", "/v2/stocks/snapshots", params=params)
        
        return {
            symbol: Snapshot.from_dict(symbol, snap_data)
            for symbol, snap_data in data.items()
        }
    
    def get_stock_snapshot(self, symbol: str, feed: str = "iex") -> Snapshot:
        """
        Get latest snapshot for a single stock.
        
        Args:
            symbol: Stock symbol
            feed: 'iex' or 'sip'
        
        Returns:
            Snapshot object
        """
        params = {"feed": feed}
        data = self._request("GET", f"/v2/stocks/{symbol.upper()}/snapshot", params=params)
        return Snapshot.from_dict(symbol.upper(), data)
    
    def get_latest_trade(self, symbol: str, feed: str = "iex") -> Trade:
        """Get latest trade for a symbol."""
        snapshot = self.get_stock_snapshot(symbol, feed)
        if snapshot.latest_trade:
            return snapshot.latest_trade
        raise ValueError(f"No trade data available for {symbol}")
    
    def get_latest_quote(self, symbol: str, feed: str = "iex") -> Quote:
        """Get latest quote for a symbol."""
        snapshot = self.get_stock_snapshot(symbol, feed)
        if snapshot.latest_quote:
            return snapshot.latest_quote
        raise ValueError(f"No quote data available for {symbol}")
    
    def get_current_price(self, symbol: str, feed: str = "iex") -> Decimal:
        """Get current price for a symbol (from latest trade)."""
        return self.get_latest_trade(symbol, feed).price
    
    # ==================== STOCKS - META ====================
    
    def get_stock_exchanges(self) -> Dict[str, str]:
        """Get stock exchange codes and names."""
        return self._request("GET", "/v2/stocks/meta/exchanges")
    
    def get_trade_conditions(self, tape: str = "A") -> Dict[str, str]:
        """
        Get trade condition codes and descriptions.
        
        Args:
            tape: 'A' (NYSE), 'B' (ARCA/AMEX), 'C' (NASDAQ)
        """
        return self._request("GET", f"/v2/stocks/meta/conditions/trade", params={"tape": tape})
    
    def get_quote_conditions(self, tape: str = "A") -> Dict[str, str]:
        """
        Get quote condition codes and descriptions.
        
        Args:
            tape: 'A' (NYSE), 'B' (ARCA/AMEX), 'C' (NASDAQ)
        """
        return self._request("GET", f"/v2/stocks/meta/conditions/quote", params={"tape": tape})
    
    # ==================== CRYPTO ====================
    
    def _crypto_request(self, method: str, endpoint: str, **kwargs) -> Any:
        """Make request to crypto API (different base path)."""
        return self.client._request(method, f"/v1beta3/crypto/us{endpoint}", base_url=self.base_url, **kwargs)
    
    def get_crypto_bars(
        self,
        symbols: Union[str, List[str]],
        timeframe: str = "1Day",
        start: Optional[Union[datetime, date, str]] = None,
        end: Optional[Union[datetime, date, str]] = None,
        limit: Optional[int] = None,
        sort: str = "asc",
        page_token: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Get historical bars for crypto pairs.
        
        Args:
            symbols: Crypto pairs like 'BTC/USD', 'ETH/USD'
            timeframe: '1Min', '5Min', '15Min', '1Hour', '1Day', etc.
            start: Start time
            end: End time
            limit: Max bars per symbol
            sort: 'asc' or 'desc'
            page_token: Pagination token
        
        Returns:
            Dict with 'bars' and 'next_page_token'
        """
        if isinstance(symbols, str):
            symbols = [symbols]
        
        params = {
            "symbols": ",".join(symbols),
            "timeframe": timeframe,
            "sort": sort,
        }
        
        if start:
            params["start"] = self._parse_datetime(start)
        if end:
            params["end"] = self._parse_datetime(end)
        if limit:
            params["limit"] = limit
        if page_token:
            params["page_token"] = page_token
        
        return self._crypto_request("GET", "/bars", params=params)
    
    def get_crypto_trades(
        self,
        symbols: Union[str, List[str]],
        start: Optional[Union[datetime, date, str]] = None,
        end: Optional[Union[datetime, date, str]] = None,
        limit: Optional[int] = None,
        sort: str = "asc",
        page_token: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Get historical trades for crypto pairs."""
        if isinstance(symbols, str):
            symbols = [symbols]
        
        params = {
            "symbols": ",".join(symbols),
            "sort": sort,
        }
        
        if start:
            params["start"] = self._parse_datetime(start)
        if end:
            params["end"] = self._parse_datetime(end)
        if limit:
            params["limit"] = limit
        if page_token:
            params["page_token"] = page_token
        
        return self._crypto_request("GET", "/trades", params=params)

    def get_crypto_quotes(
        self,
        symbols: Union[str, List[str]],
        start: Optional[Union[datetime, date, str]] = None,
        end: Optional[Union[datetime, date, str]] = None,
        limit: Optional[int] = None,
        sort: str = "asc",
        page_token: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Get historical quotes for crypto pairs."""
        if isinstance(symbols, str):
            symbols = [symbols]
        
        params = {
            "symbols": ",".join(symbols),
            "sort": sort,
        }
        
        if start:
            params["start"] = self._parse_datetime(start)
        if end:
            params["end"] = self._parse_datetime(end)
        if limit:
            params["limit"] = limit
        if page_token:
            params["page_token"] = page_token
        
        return self._crypto_request("GET", "/quotes", params=params)
    
    def get_crypto_snapshots(
        self,
        symbols: Union[str, List[str]],
    ) -> Dict[str, Snapshot]:
        """Get latest snapshots for crypto pairs."""
        if isinstance(symbols, str):
            symbols = [symbols]
        
        params = {"symbols": ",".join(symbols)}
        data = self._crypto_request("GET", "/snapshots", params=params)
        
        return {
            symbol: Snapshot.from_dict(symbol, snap_data)
            for symbol, snap_data in data.get("snapshots", {}).items()
        }
    
    def get_crypto_snapshot(self, symbol: str) -> Snapshot:
        """Get latest snapshot for a single crypto pair."""
        snapshots = self.get_crypto_snapshots([symbol])
        if symbol in snapshots:
            return snapshots[symbol]
        raise ValueError(f"No snapshot for {symbol}")
    
    def get_crypto_symbols(self) -> List[str]:
        """Get list of available crypto symbols."""
        # Note: This endpoint may not exist in v1beta3, return common pairs
        return ["BTC/USD", "ETH/USD", "LTC/USD", "BCH/USD", "DOGE/USD", "SHIB/USD", "AVAX/USD", "UNI/USD"]
    
    def get_crypto_price(self, symbol: str) -> Decimal:
        """Get current price for a crypto pair."""
        snapshot = self.get_crypto_snapshot(symbol)
        if snapshot.latest_trade:
            return snapshot.latest_trade.price
        raise ValueError(f"No trade data available for {symbol}")
    
    # ==================== OPTIONS (BETA) ====================
    
    def get_options_contracts(
        self,
        underlying_symbols: Optional[Union[str, List[str]]] = None,
        status: str = "active",
        expiration_date: Optional[Union[date, str]] = None,
        expiration_date_gte: Optional[Union[date, str]] = None,
        expiration_date_lte: Optional[Union[date, str]] = None,
        root_symbol: Optional[str] = None,
        type: Optional[str] = None,
        strike_price_gte: Optional[Union[float, Decimal]] = None,
        strike_price_lte: Optional[Union[float, Decimal]] = None,
        limit: int = 100,
        page_token: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Get options contracts.
        
        Args:
            underlying_symbols: Filter by underlying symbols
            status: 'active' or 'inactive'
            expiration_date: Exact expiration date
            expiration_date_gte: Expiration >= date
            expiration_date_lte: Expiration <= date
            root_symbol: Options root symbol
            type: 'call' or 'put'
            strike_price_gte: Strike >= price
            strike_price_lte: Strike <= price
            limit: Max results (default 100)
            page_token: Pagination token
        
        Returns:
            Dict with 'option_contracts' and 'next_page_token'
        """
        params = {"status": status, "limit": limit}
        
        if underlying_symbols:
            if isinstance(underlying_symbols, str):
                underlying_symbols = [underlying_symbols]
            params["underlying_symbols"] = ",".join(underlying_symbols)
        if expiration_date:
            params["expiration_date"] = expiration_date if isinstance(expiration_date, str) else expiration_date.isoformat()
        if expiration_date_gte:
            params["expiration_date_gte"] = expiration_date_gte if isinstance(expiration_date_gte, str) else expiration_date_gte.isoformat()
        if expiration_date_lte:
            params["expiration_date_lte"] = expiration_date_lte if isinstance(expiration_date_lte, str) else expiration_date_lte.isoformat()
        if root_symbol:
            params["root_symbol"] = root_symbol
        if type:
            params["type"] = type
        if strike_price_gte:
            params["strike_price_gte"] = str(strike_price_gte)
        if strike_price_lte:
            params["strike_price_lte"] = str(strike_price_lte)
        if page_token:
            params["page_token"] = page_token
        
        # Options contracts are on Trading API, not Market Data
        return self.client._request("GET", "/v2/options/contracts", params=params)
    
    def get_options_contract(self, symbol_or_id: str) -> Dict[str, Any]:
        """Get options contract by symbol or ID."""
        return self.client._request("GET", f"/v2/options/contracts/{symbol_or_id}")

    def get_options_bars(
        self,
        symbols: Union[str, List[str]],
        timeframe: str = "1Day",
        start: Optional[Union[datetime, date, str]] = None,
        end: Optional[Union[datetime, date, str]] = None,
        limit: Optional[int] = None,
        sort: str = "asc",
        page_token: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Get historical bars for options contracts."""
        if isinstance(symbols, str):
            symbols = [symbols]
        
        params = {
            "symbols": ",".join(symbols),
            "timeframe": timeframe,
            "sort": sort,
        }
        
        if start:
            params["start"] = self._parse_datetime(start)
        if end:
            params["end"] = self._parse_datetime(end)
        if limit:
            params["limit"] = limit
        if page_token:
            params["page_token"] = page_token
        
        return self._request("GET", "/v1beta1/options/bars", params=params)
    
    def get_options_trades(
        self,
        symbols: Union[str, List[str]],
        start: Optional[Union[datetime, date, str]] = None,
        end: Optional[Union[datetime, date, str]] = None,
        limit: Optional[int] = None,
        sort: str = "asc",
        page_token: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Get historical trades for options contracts."""
        if isinstance(symbols, str):
            symbols = [symbols]
        
        params = {
            "symbols": ",".join(symbols),
            "sort": sort,
        }
        
        if start:
            params["start"] = self._parse_datetime(start)
        if end:
            params["end"] = self._parse_datetime(end)
        if limit:
            params["limit"] = limit
        if page_token:
            params["page_token"] = page_token
        
        return self._request("GET", "/v1beta1/options/trades", params=params)
    
    def get_options_quotes(
        self,
        symbols: Union[str, List[str]],
        start: Optional[Union[datetime, date, str]] = None,
        end: Optional[Union[datetime, date, str]] = None,
        limit: Optional[int] = None,
        sort: str = "asc",
        page_token: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Get historical quotes for options contracts."""
        if isinstance(symbols, str):
            symbols = [symbols]
        
        params = {
            "symbols": ",".join(symbols),
            "sort": sort,
        }
        
        if start:
            params["start"] = self._parse_datetime(start)
        if end:
            params["end"] = self._parse_datetime(end)
        if limit:
            params["limit"] = limit
        if page_token:
            params["page_token"] = page_token
        
        return self._request("GET", "/v1beta1/options/quotes", params=params)
    
    def get_options_snapshots(self, underlying_symbol: str) -> Dict[str, Any]:
        """
        Get options snapshots for an underlying symbol.
        
        Args:
            underlying_symbol: Stock symbol (e.g., 'AAPL')
        
        Returns:
            Dict with options chain snapshots
        """
        return self._request("GET", f"/v1beta1/options/snapshots/{underlying_symbol.upper()}")
    
    # ==================== UTILITY METHODS ====================
    
    def get_multi_stock_prices(self, symbols: List[str]) -> Dict[str, Decimal]:
        """
        Get current prices for multiple stocks.
        
        Args:
            symbols: List of stock symbols
        
        Returns:
            Dict mapping symbol to current price
        """
        snapshots = self.get_stock_snapshots(symbols)
        prices = {}
        
        for symbol, snapshot in snapshots.items():
            if snapshot.latest_trade:
                prices[symbol] = snapshot.latest_trade.price
        
        return prices
    
    def get_daily_bars(
        self,
        symbol: str,
        days: int = 30,
        adjustment: str = "split",
    ) -> List[Bar]:
        """
        Get last N days of daily bars for a symbol.
        
        Args:
            symbol: Stock symbol
            days: Number of days
            adjustment: Price adjustment type
        
        Returns:
            List of Bar objects
        """
        from datetime import timedelta
        
        end = datetime.now()
        start = end - timedelta(days=days + 10)  # Extra days for weekends/holidays
        
        bars = self.get_all_stock_bars(
            symbols=symbol,
            timeframe="1Day",
            start=start,
            end=end,
            adjustment=adjustment,
            limit=days,
        )
        
        return bars.get(symbol.upper(), [])[-days:]
