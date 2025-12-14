"""
Alpaca Markets API - Base Client with retry, rate limiting, error handling
"""
import time
import logging
from typing import Optional, Dict, Any, Callable
from functools import wraps

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from .exceptions import (
    AlpacaError,
    AuthenticationError,
    ForbiddenError,
    NotFoundError,
    RateLimitError,
    ValidationError,
    APIError,
)

logger = logging.getLogger(__name__)


def retry_on_rate_limit(max_retries: int = 3, base_delay: float = 1.0):
    """Decorator for automatic retry on rate limit."""
    def decorator(func: Callable):
        @wraps(func)
        def wrapper(*args, **kwargs):
            last_exception = None
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except RateLimitError as e:
                    last_exception = e
                    delay = e.retry_after or (base_delay * (2 ** attempt))
                    logger.warning(f"Rate limited. Retrying in {delay}s (attempt {attempt + 1}/{max_retries})")
                    time.sleep(delay)
            raise last_exception
        return wrapper
    return decorator


class AlpacaClient:
    """
    Base client for Alpaca API with authentication, retry logic, and error handling.
    
    Features:
    - Automatic retry on connection errors
    - Rate limit handling with exponential backoff
    - Detailed error messages
    - Request/response logging
    - Connection pooling
    """
    
    # Base URLs
    TRADING_LIVE = "https://api.alpaca.markets"
    TRADING_PAPER = "https://paper-api.alpaca.markets"
    MARKET_DATA = "https://data.alpaca.markets"
    BROKER_SANDBOX = "https://broker-api.sandbox.alpaca.markets"
    BROKER_PRODUCTION = "https://broker-api.alpaca.markets"

    def __init__(
        self,
        api_key: str,
        api_secret: str,
        paper: bool = True,
        timeout: int = 30,
        max_retries: int = 3,
        retry_backoff: float = 0.5,
        pool_connections: int = 10,
        pool_maxsize: int = 10,
    ):
        """
        Initialize Alpaca client.
        
        Args:
            api_key: APCA-API-KEY-ID
            api_secret: APCA-API-SECRET-KEY
            paper: Use paper trading (default True)
            timeout: Request timeout in seconds
            max_retries: Max retry attempts for failed requests
            retry_backoff: Backoff factor for retries
            pool_connections: Number of connection pools
            pool_maxsize: Max connections per pool
        """
        if not api_key or not api_secret:
            raise ValueError("API key and secret are required")
        
        self.api_key = api_key
        self.api_secret = api_secret
        self.paper = paper
        self.timeout = timeout
        self.base_url = self.TRADING_PAPER if paper else self.TRADING_LIVE
        
        # Setup session with retry strategy
        self.session = requests.Session()
        
        retry_strategy = Retry(
            total=max_retries,
            backoff_factor=retry_backoff,
            status_forcelist=[500, 502, 503, 504],
            allowed_methods=["GET", "POST", "PATCH", "DELETE", "PUT"],
        )
        
        adapter = HTTPAdapter(
            max_retries=retry_strategy,
            pool_connections=pool_connections,
            pool_maxsize=pool_maxsize,
        )
        
        self.session.mount("https://", adapter)
        self.session.mount("http://", adapter)
        
        self.session.headers.update({
            "APCA-API-KEY-ID": api_key,
            "APCA-API-SECRET-KEY": api_secret,
            "Content-Type": "application/json",
            "Accept": "application/json",
        })
        
        # Rate limiting state
        self._last_request_time = 0
        self._min_request_interval = 0.1  # 100ms between requests
    
    def _handle_error(self, response: requests.Response) -> None:
        """Parse and raise appropriate exception for error responses."""
        status_code = response.status_code
        
        try:
            error_data = response.json()
            message = error_data.get("message", response.text)
            code = error_data.get("code", "")
        except Exception:
            message = response.text or f"HTTP {status_code}"
            error_data = {}
            code = ""
        
        error_kwargs = {
            "message": message,
            "status_code": status_code,
            "response": error_data,
        }
        
        if status_code == 401:
            raise AuthenticationError(**error_kwargs)
        elif status_code == 403:
            raise ForbiddenError(**error_kwargs)
        elif status_code == 404:
            raise NotFoundError(**error_kwargs)
        elif status_code == 422:
            raise ValidationError(**error_kwargs)
        elif status_code == 429:
            retry_after = response.headers.get("Retry-After")
            raise RateLimitError(
                retry_after=int(retry_after) if retry_after else None,
                **error_kwargs
            )
        elif status_code >= 500:
            raise APIError(**error_kwargs)
        else:
            raise AlpacaError(**error_kwargs)

    def _rate_limit(self) -> None:
        """Simple rate limiting between requests."""
        elapsed = time.time() - self._last_request_time
        if elapsed < self._min_request_interval:
            time.sleep(self._min_request_interval - elapsed)
        self._last_request_time = time.time()
    
    @retry_on_rate_limit(max_retries=3)
    def _request(
        self,
        method: str,
        endpoint: str,
        base_url: Optional[str] = None,
        params: Optional[Dict] = None,
        data: Optional[Dict] = None,
        timeout: Optional[int] = None,
    ) -> Any:
        """
        Make HTTP request to Alpaca API.
        
        Args:
            method: HTTP method (GET, POST, PATCH, DELETE, PUT)
            endpoint: API endpoint path
            base_url: Override base URL (for market data, broker API)
            params: Query parameters
            data: Request body (JSON)
            timeout: Override default timeout
        
        Returns:
            Parsed JSON response or None
        
        Raises:
            AlpacaError: On API errors
        """
        self._rate_limit()
        
        url = f"{base_url or self.base_url}{endpoint}"
        
        logger.debug(f"{method} {url} params={params} data={data}")
        
        try:
            response = self.session.request(
                method=method,
                url=url,
                params=params,
                json=data,
                timeout=timeout or self.timeout,
            )
        except requests.exceptions.Timeout:
            raise AlpacaError(f"Request timeout after {self.timeout}s: {method} {endpoint}")
        except requests.exceptions.ConnectionError as e:
            raise AlpacaError(f"Connection error: {e}")
        except requests.exceptions.RequestException as e:
            raise AlpacaError(f"Request failed: {e}")
        
        logger.debug(f"Response {response.status_code}: {response.text[:500] if response.text else 'empty'}")
        
        if not response.ok:
            self._handle_error(response)
        
        if response.content:
            return response.json()
        return None
    
    def get(self, endpoint: str, **kwargs) -> Any:
        """GET request."""
        return self._request("GET", endpoint, **kwargs)
    
    def post(self, endpoint: str, **kwargs) -> Any:
        """POST request."""
        return self._request("POST", endpoint, **kwargs)
    
    def patch(self, endpoint: str, **kwargs) -> Any:
        """PATCH request."""
        return self._request("PATCH", endpoint, **kwargs)
    
    def delete(self, endpoint: str, **kwargs) -> Any:
        """DELETE request."""
        return self._request("DELETE", endpoint, **kwargs)
    
    def put(self, endpoint: str, **kwargs) -> Any:
        """PUT request."""
        return self._request("PUT", endpoint, **kwargs)
    
    def close(self) -> None:
        """Close the session."""
        self.session.close()
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
        return False
