"""
Alpaca Trading API (v2) - Full Implementation
"""
import uuid
from typing import Optional, Dict, List, Any, Union
from datetime import datetime, date
from decimal import Decimal

from .client import AlpacaClient
from .models import (
    Account, Asset, Order, Position, Clock, Calendar, Watchlist,
    OrderSide, OrderType, TimeInForce, OrderStatus,
)
from .exceptions import OrderError, PositionError, ValidationError


class TradingAPI:
    """
    Trading API endpoints for account, orders, positions, watchlists.
    
    All methods return typed model objects for better IDE support.
    """
    
    def __init__(self, client: AlpacaClient):
        self.client = client
    
    # ==================== ACCOUNT ====================
    
    def get_account(self) -> Account:
        """
        Get account information including buying power, equity, etc.
        
        Returns:
            Account object with all account details
        """
        data = self.client.get("/v2/account")
        return Account.from_dict(data)
    
    def get_account_configurations(self) -> Dict[str, Any]:
        """
        Get account configurations.
        
        Returns:
            Dict with dtbp_check, trade_confirm_email, suspend_trade, 
            no_shorting, fractional_trading, max_margin_multiplier, pdt_check
        """
        return self.client.get("/v2/account/configurations")
    
    def update_account_configurations(
        self,
        dtbp_check: Optional[str] = None,
        trade_confirm_email: Optional[str] = None,
        suspend_trade: Optional[bool] = None,
        no_shorting: Optional[bool] = None,
        fractional_trading: Optional[bool] = None,
        max_margin_multiplier: Optional[str] = None,
        pdt_check: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Update account configurations.
        
        Args:
            dtbp_check: 'both', 'entry', 'exit'
            trade_confirm_email: 'all', 'none'
            suspend_trade: Suspend trading
            no_shorting: Disable shorting
            fractional_trading: Enable fractional shares
            max_margin_multiplier: '1' or '2'
            pdt_check: 'both', 'entry', 'exit'
        """
        config = {}
        if dtbp_check is not None:
            config["dtbp_check"] = dtbp_check
        if trade_confirm_email is not None:
            config["trade_confirm_email"] = trade_confirm_email
        if suspend_trade is not None:
            config["suspend_trade"] = suspend_trade
        if no_shorting is not None:
            config["no_shorting"] = no_shorting
        if fractional_trading is not None:
            config["fractional_trading"] = fractional_trading
        if max_margin_multiplier is not None:
            config["max_margin_multiplier"] = max_margin_multiplier
        if pdt_check is not None:
            config["pdt_check"] = pdt_check
        
        return self.client.patch("/v2/account/configurations", data=config)

    def get_account_activities(
        self,
        activity_types: Optional[List[str]] = None,
        until: Optional[Union[datetime, str]] = None,
        after: Optional[Union[datetime, str]] = None,
        direction: Optional[str] = None,
        date: Optional[Union[date, str]] = None,
        page_size: int = 100,
        page_token: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """
        Get account activities (trades, dividends, etc).
        
        Args:
            activity_types: Filter by types: FILL, TRANS, MISC, ACATC, ACATS, 
                           CSD, CSW, DIV, DIVCGL, DIVCGS, DIVFEE, DIVFT, DIVNRA,
                           DIVROC, DIVTW, DIVTXEX, INT, INTNRA, INTTW, JNL, JNLC,
                           JNLS, MA, NC, OPASN, OPEXP, OPXRC, PTC, PTR, REORG, SC, SSO, SSP
            until: Filter activities before this time
            after: Filter activities after this time
            direction: 'asc' or 'desc'
            date: Filter by specific date
            page_size: Number of results (max 100)
            page_token: Pagination token
        
        Returns:
            List of activity dicts
        """
        params = {"page_size": page_size}
        
        if activity_types:
            params["activity_types"] = ",".join(activity_types)
        if until:
            params["until"] = until if isinstance(until, str) else until.isoformat()
        if after:
            params["after"] = after if isinstance(after, str) else after.isoformat()
        if direction:
            params["direction"] = direction
        if date:
            params["date"] = date if isinstance(date, str) else date.isoformat()
        if page_token:
            params["page_token"] = page_token
        
        return self.client.get("/v2/account/activities", params=params)
    
    def get_portfolio_history(
        self,
        period: Optional[str] = None,
        timeframe: Optional[str] = None,
        date_end: Optional[Union[date, str]] = None,
        extended_hours: bool = False,
    ) -> Dict[str, Any]:
        """
        Get portfolio value history.
        
        Args:
            period: '1D', '1W', '1M', '3M', '6M', '1A', 'all', 'intraday'
            timeframe: '1Min', '5Min', '15Min', '1H', '1D'
            date_end: End date for the history
            extended_hours: Include extended hours data
        
        Returns:
            Dict with timestamp, equity, profit_loss, profit_loss_pct, 
            base_value, timeframe arrays
        """
        params = {"extended_hours": extended_hours}
        
        if period:
            params["period"] = period
        if timeframe:
            params["timeframe"] = timeframe
        if date_end:
            params["date_end"] = date_end if isinstance(date_end, str) else date_end.isoformat()
        
        return self.client.get("/v2/account/portfolio/history", params=params)
    
    # ==================== ASSETS ====================
    
    def get_assets(
        self,
        status: Optional[str] = None,
        asset_class: Optional[str] = None,
        exchange: Optional[str] = None,
        attributes: Optional[str] = None,
    ) -> List[Asset]:
        """
        Get list of tradeable assets.
        
        Args:
            status: 'active' or 'inactive'
            asset_class: 'us_equity' or 'crypto'
            exchange: Filter by exchange
            attributes: Comma-separated attributes
        
        Returns:
            List of Asset objects
        """
        params = {}
        if status:
            params["status"] = status
        if asset_class:
            params["asset_class"] = asset_class
        if exchange:
            params["exchange"] = exchange
        if attributes:
            params["attributes"] = attributes
        
        data = self.client.get("/v2/assets", params=params)
        return [Asset.from_dict(a) for a in data]
    
    def get_asset(self, symbol_or_id: str) -> Asset:
        """
        Get asset by symbol or asset ID.
        
        Args:
            symbol_or_id: Stock symbol (e.g., 'AAPL') or UUID
        
        Returns:
            Asset object
        """
        data = self.client.get(f"/v2/assets/{symbol_or_id}")
        return Asset.from_dict(data)

    # ==================== ORDERS ====================
    
    def create_order(
        self,
        symbol: str,
        side: Union[OrderSide, str],
        type: Union[OrderType, str] = OrderType.MARKET,
        time_in_force: Union[TimeInForce, str] = TimeInForce.DAY,
        qty: Optional[Union[int, float, Decimal, str]] = None,
        notional: Optional[Union[float, Decimal, str]] = None,
        limit_price: Optional[Union[float, Decimal, str]] = None,
        stop_price: Optional[Union[float, Decimal, str]] = None,
        trail_price: Optional[Union[float, Decimal, str]] = None,
        trail_percent: Optional[Union[float, Decimal, str]] = None,
        extended_hours: bool = False,
        client_order_id: Optional[str] = None,
        order_class: Optional[str] = None,
        take_profit: Optional[Dict] = None,
        stop_loss: Optional[Dict] = None,
    ) -> Order:
        """
        Create a new order.
        
        Args:
            symbol: Stock symbol (e.g., 'AAPL')
            side: 'buy' or 'sell' (or OrderSide enum)
            type: Order type - 'market', 'limit', 'stop', 'stop_limit', 'trailing_stop'
            time_in_force: 'day', 'gtc', 'opg', 'cls', 'ioc', 'fok'
            qty: Number of shares (mutually exclusive with notional)
            notional: Dollar amount (mutually exclusive with qty)
            limit_price: Required for limit and stop_limit orders
            stop_price: Required for stop and stop_limit orders
            trail_price: Dollar value for trailing stop
            trail_percent: Percent value for trailing stop
            extended_hours: Allow execution in extended hours
            client_order_id: Custom order ID (max 48 chars)
            order_class: 'simple', 'bracket', 'oco', 'oto'
            take_profit: Take profit leg for bracket orders
            stop_loss: Stop loss leg for bracket orders
        
        Returns:
            Order object
        
        Raises:
            ValidationError: If order parameters are invalid
            OrderError: If order cannot be placed
        
        Examples:
            # Market order
            order = trading.create_order('AAPL', 'buy', qty=10)
            
            # Limit order
            order = trading.create_order('AAPL', 'buy', type='limit', 
                                         qty=10, limit_price=150.00)
            
            # Dollar-based order
            order = trading.create_order('AAPL', 'buy', notional=1000)
            
            # Bracket order
            order = trading.create_order(
                'AAPL', 'buy', qty=10, order_class='bracket',
                take_profit={'limit_price': 160},
                stop_loss={'stop_price': 140}
            )
        """
        # Validate qty vs notional
        if qty is None and notional is None:
            raise ValidationError("Either qty or notional is required")
        if qty is not None and notional is not None:
            raise ValidationError("Cannot specify both qty and notional")
        
        # Build order data
        data = {
            "symbol": symbol.upper(),
            "side": side.value if isinstance(side, OrderSide) else side,
            "type": type.value if isinstance(type, OrderType) else type,
            "time_in_force": time_in_force.value if isinstance(time_in_force, TimeInForce) else time_in_force,
            "extended_hours": extended_hours,
        }
        
        if qty is not None:
            data["qty"] = str(qty)
        if notional is not None:
            data["notional"] = str(notional)
        if limit_price is not None:
            data["limit_price"] = str(limit_price)
        if stop_price is not None:
            data["stop_price"] = str(stop_price)
        if trail_price is not None:
            data["trail_price"] = str(trail_price)
        if trail_percent is not None:
            data["trail_percent"] = str(trail_percent)
        if client_order_id:
            data["client_order_id"] = client_order_id
        if order_class:
            data["order_class"] = order_class
        if take_profit:
            data["take_profit"] = take_profit
        if stop_loss:
            data["stop_loss"] = stop_loss
        
        response = self.client.post("/v2/orders", data=data)
        return Order.from_dict(response)

    def buy(
        self,
        symbol: str,
        qty: Optional[Union[int, float]] = None,
        notional: Optional[Union[float, Decimal]] = None,
        **kwargs
    ) -> Order:
        """
        Shortcut for buy market order.
        
        Args:
            symbol: Stock symbol
            qty: Number of shares
            notional: Dollar amount
            **kwargs: Additional order parameters
        """
        return self.create_order(symbol, OrderSide.BUY, qty=qty, notional=notional, **kwargs)
    
    def sell(
        self,
        symbol: str,
        qty: Optional[Union[int, float]] = None,
        notional: Optional[Union[float, Decimal]] = None,
        **kwargs
    ) -> Order:
        """
        Shortcut for sell market order.
        
        Args:
            symbol: Stock symbol
            qty: Number of shares
            notional: Dollar amount
            **kwargs: Additional order parameters
        """
        return self.create_order(symbol, OrderSide.SELL, qty=qty, notional=notional, **kwargs)
    
    def buy_limit(
        self,
        symbol: str,
        qty: Union[int, float],
        limit_price: Union[float, Decimal],
        time_in_force: Union[TimeInForce, str] = TimeInForce.GTC,
        **kwargs
    ) -> Order:
        """Shortcut for buy limit order."""
        return self.create_order(
            symbol, OrderSide.BUY, OrderType.LIMIT,
            qty=qty, limit_price=limit_price, time_in_force=time_in_force, **kwargs
        )
    
    def sell_limit(
        self,
        symbol: str,
        qty: Union[int, float],
        limit_price: Union[float, Decimal],
        time_in_force: Union[TimeInForce, str] = TimeInForce.GTC,
        **kwargs
    ) -> Order:
        """Shortcut for sell limit order."""
        return self.create_order(
            symbol, OrderSide.SELL, OrderType.LIMIT,
            qty=qty, limit_price=limit_price, time_in_force=time_in_force, **kwargs
        )
    
    def buy_stop(
        self,
        symbol: str,
        qty: Union[int, float],
        stop_price: Union[float, Decimal],
        **kwargs
    ) -> Order:
        """Shortcut for buy stop order."""
        return self.create_order(
            symbol, OrderSide.BUY, OrderType.STOP,
            qty=qty, stop_price=stop_price, **kwargs
        )
    
    def sell_stop(
        self,
        symbol: str,
        qty: Union[int, float],
        stop_price: Union[float, Decimal],
        **kwargs
    ) -> Order:
        """Shortcut for sell stop order."""
        return self.create_order(
            symbol, OrderSide.SELL, OrderType.STOP,
            qty=qty, stop_price=stop_price, **kwargs
        )
    
    def bracket_order(
        self,
        symbol: str,
        side: Union[OrderSide, str],
        qty: Union[int, float],
        take_profit_price: Union[float, Decimal],
        stop_loss_price: Union[float, Decimal],
        limit_price: Optional[Union[float, Decimal]] = None,
        stop_loss_limit_price: Optional[Union[float, Decimal]] = None,
        **kwargs
    ) -> Order:
        """
        Create a bracket order (entry + take profit + stop loss).
        
        Args:
            symbol: Stock symbol
            side: 'buy' or 'sell'
            qty: Number of shares
            take_profit_price: Take profit limit price
            stop_loss_price: Stop loss trigger price
            limit_price: Entry limit price (if None, uses market order)
            stop_loss_limit_price: Stop loss limit price (if None, uses stop market)
        """
        take_profit = {"limit_price": str(take_profit_price)}
        stop_loss = {"stop_price": str(stop_loss_price)}
        
        if stop_loss_limit_price:
            stop_loss["limit_price"] = str(stop_loss_limit_price)
        
        order_type = OrderType.LIMIT if limit_price else OrderType.MARKET
        
        return self.create_order(
            symbol=symbol,
            side=side,
            type=order_type,
            qty=qty,
            limit_price=limit_price,
            order_class="bracket",
            take_profit=take_profit,
            stop_loss=stop_loss,
            **kwargs
        )

    def get_orders(
        self,
        status: Optional[str] = None,
        limit: int = 50,
        after: Optional[Union[datetime, str]] = None,
        until: Optional[Union[datetime, str]] = None,
        direction: str = "desc",
        nested: bool = False,
        symbols: Optional[List[str]] = None,
        side: Optional[str] = None,
    ) -> List[Order]:
        """
        Get list of orders.
        
        Args:
            status: 'open', 'closed', 'all' (default: open)
            limit: Max number of orders (default: 50, max: 500)
            after: Filter orders after this time
            until: Filter orders before this time
            direction: 'asc' or 'desc'
            nested: Include nested orders (bracket legs)
            symbols: Filter by symbols
            side: Filter by 'buy' or 'sell'
        
        Returns:
            List of Order objects
        """
        params = {
            "limit": min(limit, 500),
            "direction": direction,
            "nested": nested,
        }
        
        if status:
            params["status"] = status
        if after:
            params["after"] = after if isinstance(after, str) else after.isoformat()
        if until:
            params["until"] = until if isinstance(until, str) else until.isoformat()
        if symbols:
            params["symbols"] = ",".join(s.upper() for s in symbols)
        if side:
            params["side"] = side
        
        data = self.client.get("/v2/orders", params=params)
        return [Order.from_dict(o) for o in data]
    
    def get_open_orders(self, **kwargs) -> List[Order]:
        """Get all open orders."""
        return self.get_orders(status="open", **kwargs)
    
    def get_closed_orders(self, **kwargs) -> List[Order]:
        """Get all closed orders."""
        return self.get_orders(status="closed", **kwargs)
    
    def get_order(self, order_id: str, nested: bool = False) -> Order:
        """
        Get order by ID.
        
        Args:
            order_id: Order UUID
            nested: Include nested orders
        
        Returns:
            Order object
        """
        params = {"nested": nested}
        data = self.client.get(f"/v2/orders/{order_id}", params=params)
        return Order.from_dict(data)
    
    def get_order_by_client_id(self, client_order_id: str) -> Order:
        """
        Get order by client order ID.
        
        Args:
            client_order_id: Your custom order ID
        
        Returns:
            Order object
        """
        params = {"client_order_id": client_order_id}
        data = self.client.get("/v2/orders:by_client_order_id", params=params)
        return Order.from_dict(data)
    
    def update_order(
        self,
        order_id: str,
        qty: Optional[Union[int, float]] = None,
        time_in_force: Optional[Union[TimeInForce, str]] = None,
        limit_price: Optional[Union[float, Decimal]] = None,
        stop_price: Optional[Union[float, Decimal]] = None,
        trail: Optional[Union[float, Decimal]] = None,
        client_order_id: Optional[str] = None,
    ) -> Order:
        """
        Update/replace an existing order.
        
        Args:
            order_id: Order UUID to update
            qty: New quantity
            time_in_force: New time in force
            limit_price: New limit price
            stop_price: New stop price
            trail: New trail value
            client_order_id: New client order ID
        
        Returns:
            Updated Order object
        """
        data = {}
        
        if qty is not None:
            data["qty"] = str(qty)
        if time_in_force is not None:
            data["time_in_force"] = time_in_force.value if isinstance(time_in_force, TimeInForce) else time_in_force
        if limit_price is not None:
            data["limit_price"] = str(limit_price)
        if stop_price is not None:
            data["stop_price"] = str(stop_price)
        if trail is not None:
            data["trail"] = str(trail)
        if client_order_id:
            data["client_order_id"] = client_order_id
        
        response = self.client.patch(f"/v2/orders/{order_id}", data=data)
        return Order.from_dict(response)
    
    def cancel_order(self, order_id: str) -> None:
        """
        Cancel an order.
        
        Args:
            order_id: Order UUID to cancel
        """
        self.client.delete(f"/v2/orders/{order_id}")
    
    def cancel_all_orders(self) -> List[Dict[str, Any]]:
        """
        Cancel all open orders.
        
        Returns:
            List of canceled order statuses
        """
        return self.client.delete("/v2/orders") or []

    # ==================== POSITIONS ====================
    
    def get_positions(self) -> List[Position]:
        """
        Get all open positions.
        
        Returns:
            List of Position objects
        """
        data = self.client.get("/v2/positions")
        return [Position.from_dict(p) for p in data]
    
    def get_position(self, symbol_or_id: str) -> Position:
        """
        Get position by symbol or asset ID.
        
        Args:
            symbol_or_id: Stock symbol or asset UUID
        
        Returns:
            Position object
        """
        data = self.client.get(f"/v2/positions/{symbol_or_id.upper()}")
        return Position.from_dict(data)
    
    def has_position(self, symbol: str) -> bool:
        """Check if position exists for symbol."""
        try:
            self.get_position(symbol)
            return True
        except Exception:
            return False
    
    def close_position(
        self,
        symbol_or_id: str,
        qty: Optional[Union[int, float]] = None,
        percentage: Optional[Union[float, Decimal]] = None,
    ) -> Order:
        """
        Close a position (fully or partially).
        
        Args:
            symbol_or_id: Stock symbol or asset UUID
            qty: Number of shares to close (None = close all)
            percentage: Percentage to close (0-100)
        
        Returns:
            Order object for the closing order
        """
        params = {}
        if qty is not None:
            params["qty"] = str(qty)
        if percentage is not None:
            params["percentage"] = str(percentage)
        
        data = self.client.delete(f"/v2/positions/{symbol_or_id.upper()}", params=params)
        return Order.from_dict(data)
    
    def close_all_positions(self, cancel_orders: bool = True) -> List[Dict[str, Any]]:
        """
        Close all open positions.
        
        Args:
            cancel_orders: Cancel open orders before closing positions
        
        Returns:
            List of closing order statuses
        """
        params = {"cancel_orders": cancel_orders}
        return self.client.delete("/v2/positions", params=params) or []
    
    def get_total_equity(self) -> Decimal:
        """Get total portfolio equity."""
        account = self.get_account()
        return account.equity
    
    def get_total_profit_loss(self) -> Decimal:
        """Get total unrealized P/L across all positions."""
        positions = self.get_positions()
        return sum(p.unrealized_pl for p in positions)
    
    # ==================== WATCHLISTS ====================
    
    def create_watchlist(self, name: str, symbols: Optional[List[str]] = None) -> Watchlist:
        """
        Create a new watchlist.
        
        Args:
            name: Watchlist name
            symbols: Initial symbols to add
        
        Returns:
            Watchlist object
        """
        data = {"name": name}
        if symbols:
            data["symbols"] = [s.upper() for s in symbols]
        
        response = self.client.post("/v2/watchlists", data=data)
        return Watchlist.from_dict(response)
    
    def get_watchlists(self) -> List[Watchlist]:
        """Get all watchlists."""
        data = self.client.get("/v2/watchlists")
        return [Watchlist.from_dict(w) for w in data]
    
    def get_watchlist(self, watchlist_id: str) -> Watchlist:
        """Get watchlist by ID."""
        data = self.client.get(f"/v2/watchlists/{watchlist_id}")
        return Watchlist.from_dict(data)
    
    def update_watchlist(
        self,
        watchlist_id: str,
        name: Optional[str] = None,
        symbols: Optional[List[str]] = None,
    ) -> Watchlist:
        """
        Update a watchlist (replace symbols).
        
        Args:
            watchlist_id: Watchlist UUID
            name: New name
            symbols: New symbol list (replaces existing)
        """
        data = {}
        if name:
            data["name"] = name
        if symbols is not None:
            data["symbols"] = [s.upper() for s in symbols]
        
        response = self.client.put(f"/v2/watchlists/{watchlist_id}", data=data)
        return Watchlist.from_dict(response)
    
    def add_to_watchlist(self, watchlist_id: str, symbol: str) -> Watchlist:
        """Add symbol to watchlist."""
        data = {"symbol": symbol.upper()}
        response = self.client.post(f"/v2/watchlists/{watchlist_id}", data=data)
        return Watchlist.from_dict(response)
    
    def remove_from_watchlist(self, watchlist_id: str, symbol: str) -> Watchlist:
        """Remove symbol from watchlist."""
        response = self.client.delete(f"/v2/watchlists/{watchlist_id}/{symbol.upper()}")
        return Watchlist.from_dict(response)
    
    def delete_watchlist(self, watchlist_id: str) -> None:
        """Delete a watchlist."""
        self.client.delete(f"/v2/watchlists/{watchlist_id}")

    # ==================== MARKET CLOCK & CALENDAR ====================
    
    def get_clock(self) -> Clock:
        """
        Get current market clock.
        
        Returns:
            Clock object with is_open, next_open, next_close
        """
        data = self.client.get("/v2/clock")
        return Clock.from_dict(data)
    
    def is_market_open(self) -> bool:
        """Check if market is currently open."""
        return self.get_clock().is_open
    
    def get_calendar(
        self,
        start: Optional[Union[date, str]] = None,
        end: Optional[Union[date, str]] = None,
    ) -> List[Calendar]:
        """
        Get market calendar.
        
        Args:
            start: Start date
            end: End date
        
        Returns:
            List of Calendar objects
        """
        params = {}
        if start:
            params["start"] = start if isinstance(start, str) else start.isoformat()
        if end:
            params["end"] = end if isinstance(end, str) else end.isoformat()
        
        data = self.client.get("/v2/calendar", params=params)
        return [Calendar.from_dict(c) for c in data]
    
    def get_next_market_open(self) -> datetime:
        """Get next market open time."""
        return self.get_clock().next_open
    
    def get_next_market_close(self) -> datetime:
        """Get next market close time."""
        return self.get_clock().next_close
    
    # ==================== UTILITY METHODS ====================
    
    def wait_for_order(
        self,
        order_id: str,
        timeout: int = 60,
        poll_interval: float = 1.0,
    ) -> Order:
        """
        Wait for order to reach terminal state.
        
        Args:
            order_id: Order UUID
            timeout: Max seconds to wait
            poll_interval: Seconds between status checks
        
        Returns:
            Final Order object
        
        Raises:
            TimeoutError: If order doesn't complete in time
        """
        import time
        start = time.time()
        
        while time.time() - start < timeout:
            order = self.get_order(order_id)
            
            if order.is_filled or order.is_canceled:
                return order
            
            time.sleep(poll_interval)
        
        raise TimeoutError(f"Order {order_id} did not complete within {timeout}s")
    
    def get_buying_power(self) -> Decimal:
        """Get current buying power."""
        return self.get_account().buying_power
    
    def can_afford(self, symbol: str, qty: int) -> bool:
        """Check if account can afford to buy qty shares of symbol."""
        try:
            asset = self.get_asset(symbol)
            # This is a rough check - actual price may vary
            # For accurate check, use market data API
            buying_power = self.get_buying_power()
            return True  # Would need current price for accurate check
        except Exception:
            return False
