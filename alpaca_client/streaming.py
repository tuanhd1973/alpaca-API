"""
Alpaca Streaming API (WebSocket) - Full Implementation

Real-time market data streaming with automatic reconnection.
"""
import json
import asyncio
import logging
from typing import Callable, List, Optional, Dict, Any, Set
from enum import Enum
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)


class StreamType(Enum):
    """WebSocket stream endpoints."""
    IEX = "wss://stream.data.alpaca.markets/v2/iex"
    SIP = "wss://stream.data.alpaca.markets/v2/sip"
    CRYPTO = "wss://stream.data.alpaca.markets/v1beta3/crypto/us"
    PAPER_TRADING = "wss://paper-api.alpaca.markets/stream"
    LIVE_TRADING = "wss://api.alpaca.markets/stream"


class MessageType(str, Enum):
    """WebSocket message types."""
    TRADE = "t"
    QUOTE = "q"
    BAR = "b"
    DAILY_BAR = "d"
    STATUS = "s"
    LULD = "l"  # Limit Up Limit Down
    CANCEL = "x"
    CORRECTION = "c"
    TRADE_UPDATE = "trade_updates"


@dataclass
class StreamConfig:
    """Streaming configuration."""
    auto_reconnect: bool = True
    reconnect_delay: float = 1.0
    max_reconnect_delay: float = 60.0
    reconnect_attempts: int = 10
    ping_interval: float = 30.0
    ping_timeout: float = 10.0


@dataclass
class Subscription:
    """Active subscriptions."""
    trades: Set[str] = field(default_factory=set)
    quotes: Set[str] = field(default_factory=set)
    bars: Set[str] = field(default_factory=set)
    daily_bars: Set[str] = field(default_factory=set)
    statuses: Set[str] = field(default_factory=set)
    lulds: Set[str] = field(default_factory=set)


class AlpacaStream:
    """
    WebSocket streaming client for real-time market data.
    
    Features:
    - Automatic reconnection with exponential backoff
    - Multiple data type subscriptions (trades, quotes, bars)
    - Decorator-based event handlers
    - Async context manager support
    
    Requires: websockets library (pip install websockets)
    
    Example:
        stream = AlpacaStream(api_key, api_secret)
        
        @stream.on_trade
        async def handle_trade(data):
            print(f"Trade: {data}")
        
        async with stream:
            await stream.subscribe(trades=["AAPL", "MSFT"])
            await stream.run()
    """

    def __init__(
        self,
        api_key: str,
        api_secret: str,
        stream_type: StreamType = StreamType.IEX,
        config: Optional[StreamConfig] = None,
    ):
        """
        Initialize streaming client.
        
        Args:
            api_key: APCA-API-KEY-ID
            api_secret: APCA-API-SECRET-KEY
            stream_type: Type of stream (IEX, SIP, CRYPTO, etc.)
            config: Streaming configuration
        """
        self.api_key = api_key
        self.api_secret = api_secret
        self.url = stream_type.value
        self.stream_type = stream_type
        self.config = config or StreamConfig()
        
        self._ws = None
        self._handlers: Dict[str, List[Callable]] = {}
        self._subscriptions = Subscription()
        self._connected = False
        self._authenticated = False
        self._running = False
        self._reconnect_count = 0
    
    # ==================== EVENT HANDLERS ====================
    
    def on(self, event_type: str):
        """
        Register handler for specific event type.
        
        Args:
            event_type: Message type ('t', 'q', 'b', etc.)
        """
        def decorator(func: Callable):
            if event_type not in self._handlers:
                self._handlers[event_type] = []
            self._handlers[event_type].append(func)
            return func
        return decorator
    
    def on_trade(self, func: Callable):
        """Register trade handler."""
        return self.on(MessageType.TRADE.value)(func)
    
    def on_quote(self, func: Callable):
        """Register quote handler."""
        return self.on(MessageType.QUOTE.value)(func)
    
    def on_bar(self, func: Callable):
        """Register bar (minute) handler."""
        return self.on(MessageType.BAR.value)(func)
    
    def on_daily_bar(self, func: Callable):
        """Register daily bar handler."""
        return self.on(MessageType.DAILY_BAR.value)(func)
    
    def on_status(self, func: Callable):
        """Register trading status handler."""
        return self.on(MessageType.STATUS.value)(func)
    
    def on_trade_update(self, func: Callable):
        """Register trade update handler (for trading stream)."""
        return self.on(MessageType.TRADE_UPDATE.value)(func)
    
    def on_error(self, func: Callable):
        """Register error handler."""
        return self.on("error")(func)
    
    def on_connect(self, func: Callable):
        """Register connection handler."""
        return self.on("connected")(func)
    
    def on_disconnect(self, func: Callable):
        """Register disconnection handler."""
        return self.on("disconnected")(func)
    
    # ==================== CONNECTION ====================
    
    async def connect(self) -> bool:
        """
        Connect to WebSocket and authenticate.
        
        Returns:
            True if connected and authenticated successfully
        """
        try:
            import websockets
        except ImportError:
            raise ImportError("Install websockets: pip install websockets")
        
        logger.info(f"Connecting to {self.url}")
        
        try:
            self._ws = await websockets.connect(
                self.url,
                ping_interval=self.config.ping_interval,
                ping_timeout=self.config.ping_timeout,
            )
            self._connected = True
            
            # Wait for welcome message
            welcome = await self._ws.recv()
            welcome_data = json.loads(welcome)
            logger.debug(f"Welcome: {welcome_data}")
            
            # Authenticate
            auth_success = await self._authenticate()
            
            if auth_success:
                self._reconnect_count = 0
                await self._emit("connected", {"url": self.url})
                
                # Resubscribe if reconnecting
                await self._resubscribe()
            
            return auth_success
            
        except Exception as e:
            logger.error(f"Connection failed: {e}")
            await self._emit("error", {"error": str(e)})
            return False

    async def _authenticate(self) -> bool:
        """Authenticate with API credentials."""
        auth_msg = {
            "action": "auth",
            "key": self.api_key,
            "secret": self.api_secret,
        }
        
        await self._ws.send(json.dumps(auth_msg))
        response = await self._ws.recv()
        data = json.loads(response)
        
        logger.debug(f"Auth response: {data}")
        
        # Check for successful auth
        for msg in data if isinstance(data, list) else [data]:
            if msg.get("T") == "success" and msg.get("msg") == "authenticated":
                self._authenticated = True
                logger.info("Authentication successful")
                return True
            elif msg.get("T") == "error":
                logger.error(f"Authentication failed: {msg.get('msg')}")
                return False
        
        return False
    
    async def _resubscribe(self) -> None:
        """Resubscribe to previous subscriptions after reconnect."""
        if any([
            self._subscriptions.trades,
            self._subscriptions.quotes,
            self._subscriptions.bars,
            self._subscriptions.daily_bars,
        ]):
            logger.info("Resubscribing to previous subscriptions")
            await self.subscribe(
                trades=list(self._subscriptions.trades),
                quotes=list(self._subscriptions.quotes),
                bars=list(self._subscriptions.bars),
                daily_bars=list(self._subscriptions.daily_bars),
            )
    
    async def disconnect(self) -> None:
        """Close WebSocket connection."""
        self._running = False
        
        if self._ws:
            await self._ws.close()
            self._ws = None
        
        self._connected = False
        self._authenticated = False
        
        await self._emit("disconnected", {})
        logger.info("Disconnected")
    
    async def _reconnect(self) -> bool:
        """Attempt to reconnect with exponential backoff."""
        if not self.config.auto_reconnect:
            return False
        
        if self._reconnect_count >= self.config.reconnect_attempts:
            logger.error(f"Max reconnection attempts ({self.config.reconnect_attempts}) reached")
            return False
        
        self._reconnect_count += 1
        delay = min(
            self.config.reconnect_delay * (2 ** (self._reconnect_count - 1)),
            self.config.max_reconnect_delay
        )
        
        logger.info(f"Reconnecting in {delay}s (attempt {self._reconnect_count})")
        await asyncio.sleep(delay)
        
        return await self.connect()
    
    # ==================== SUBSCRIPTIONS ====================
    
    async def subscribe(
        self,
        trades: Optional[List[str]] = None,
        quotes: Optional[List[str]] = None,
        bars: Optional[List[str]] = None,
        daily_bars: Optional[List[str]] = None,
        statuses: Optional[List[str]] = None,
        lulds: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """
        Subscribe to market data streams.
        
        Args:
            trades: Symbols for trade data
            quotes: Symbols for quote data
            bars: Symbols for minute bar data
            daily_bars: Symbols for daily bar data
            statuses: Symbols for trading status
            lulds: Symbols for LULD data
        
        Returns:
            Subscription confirmation
        """
        msg = {"action": "subscribe"}
        
        if trades:
            msg["trades"] = [s.upper() for s in trades]
            self._subscriptions.trades.update(msg["trades"])
        if quotes:
            msg["quotes"] = [s.upper() for s in quotes]
            self._subscriptions.quotes.update(msg["quotes"])
        if bars:
            msg["bars"] = [s.upper() for s in bars]
            self._subscriptions.bars.update(msg["bars"])
        if daily_bars:
            msg["dailyBars"] = [s.upper() for s in daily_bars]
            self._subscriptions.daily_bars.update(msg["dailyBars"])
        if statuses:
            msg["statuses"] = [s.upper() for s in statuses]
            self._subscriptions.statuses.update(msg["statuses"])
        if lulds:
            msg["lulds"] = [s.upper() for s in lulds]
            self._subscriptions.lulds.update(msg["lulds"])
        
        await self._ws.send(json.dumps(msg))
        response = await self._ws.recv()
        
        logger.info(f"Subscribed: {msg}")
        return json.loads(response)
    
    async def unsubscribe(
        self,
        trades: Optional[List[str]] = None,
        quotes: Optional[List[str]] = None,
        bars: Optional[List[str]] = None,
        daily_bars: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """Unsubscribe from market data streams."""
        msg = {"action": "unsubscribe"}
        
        if trades:
            msg["trades"] = [s.upper() for s in trades]
            self._subscriptions.trades -= set(msg["trades"])
        if quotes:
            msg["quotes"] = [s.upper() for s in quotes]
            self._subscriptions.quotes -= set(msg["quotes"])
        if bars:
            msg["bars"] = [s.upper() for s in bars]
            self._subscriptions.bars -= set(msg["bars"])
        if daily_bars:
            msg["dailyBars"] = [s.upper() for s in daily_bars]
            self._subscriptions.daily_bars -= set(msg["dailyBars"])
        
        await self._ws.send(json.dumps(msg))
        response = await self._ws.recv()
        
        logger.info(f"Unsubscribed: {msg}")
        return json.loads(response)

    # ==================== MESSAGE HANDLING ====================
    
    async def _emit(self, event_type: str, data: Any) -> None:
        """Emit event to registered handlers."""
        handlers = self._handlers.get(event_type, [])
        
        for handler in handlers:
            try:
                if asyncio.iscoroutinefunction(handler):
                    await handler(data)
                else:
                    handler(data)
            except Exception as e:
                logger.error(f"Handler error for {event_type}: {e}")
    
    async def _handle_message(self, message: str) -> None:
        """Process incoming WebSocket message."""
        try:
            data = json.loads(message)
            
            # Handle array of messages
            messages = data if isinstance(data, list) else [data]
            
            for msg in messages:
                msg_type = msg.get("T")
                
                if msg_type == "error":
                    logger.error(f"Stream error: {msg.get('msg')}")
                    await self._emit("error", msg)
                elif msg_type == "subscription":
                    logger.debug(f"Subscription update: {msg}")
                elif msg_type in self._handlers:
                    await self._emit(msg_type, msg)
                else:
                    logger.debug(f"Unhandled message type: {msg_type}")
                    
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse message: {e}")
    
    # ==================== MAIN LOOP ====================
    
    async def run(self) -> None:
        """
        Main event loop - listen for messages until stopped.
        
        Call this after connecting and subscribing.
        """
        self._running = True
        
        while self._running:
            try:
                if not self._connected:
                    if not await self._reconnect():
                        break
                    continue
                
                message = await self._ws.recv()
                await self._handle_message(message)
                
            except Exception as e:
                if not self._running:
                    break
                    
                logger.error(f"Stream error: {e}")
                self._connected = False
                
                if self.config.auto_reconnect:
                    if not await self._reconnect():
                        break
                else:
                    break
        
        await self.disconnect()
    
    async def run_forever(self) -> None:
        """Run the stream indefinitely with auto-reconnect."""
        if not self._connected:
            await self.connect()
        await self.run()
    
    def stop(self) -> None:
        """Signal the stream to stop."""
        self._running = False
    
    # ==================== CONTEXT MANAGER ====================
    
    async def __aenter__(self):
        await self.connect()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.disconnect()
        return False
    
    # ==================== PROPERTIES ====================
    
    @property
    def is_connected(self) -> bool:
        """Check if connected."""
        return self._connected
    
    @property
    def is_authenticated(self) -> bool:
        """Check if authenticated."""
        return self._authenticated
    
    @property
    def subscriptions(self) -> Subscription:
        """Get current subscriptions."""
        return self._subscriptions


class TradingStream(AlpacaStream):
    """
    Streaming client for trading updates (order fills, etc).
    
    Example:
        stream = TradingStream(api_key, api_secret, paper=True)
        
        @stream.on_trade_update
        async def handle_update(data):
            print(f"Order update: {data}")
        
        async with stream:
            await stream.run()
    """
    
    def __init__(
        self,
        api_key: str,
        api_secret: str,
        paper: bool = True,
        config: Optional[StreamConfig] = None,
    ):
        stream_type = StreamType.PAPER_TRADING if paper else StreamType.LIVE_TRADING
        super().__init__(api_key, api_secret, stream_type, config)
    
    async def subscribe_trade_updates(self) -> Dict[str, Any]:
        """Subscribe to trade updates."""
        msg = {
            "action": "listen",
            "data": {"streams": ["trade_updates"]}
        }
        await self._ws.send(json.dumps(msg))
        response = await self._ws.recv()
        return json.loads(response)
    
    async def _resubscribe(self) -> None:
        """Resubscribe to trade updates after reconnect."""
        await self.subscribe_trade_updates()
