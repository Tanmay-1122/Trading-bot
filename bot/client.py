"""
Low-level Binance Futures Testnet REST client.

Handles:
  - HMAC-SHA256 request signing
  - Timestamping
  - HTTP session management (connection pooling, retries)
  - Raw API call logging (request params + response body)
  - Structured error propagation
"""

from __future__ import annotations

import hashlib
import hmac
import time
from typing import Any, Optional
from urllib.parse import urlencode

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from .logging_config import get_logger

logger = get_logger("client")

TESTNET_BASE_URL = "https://testnet.binancefuture.com"

# Retry on transient network errors / 5xx responses (not on 4xx – those are our fault)
_RETRY_STRATEGY = Retry(
    total=3,
    backoff_factor=0.5,
    status_forcelist=[500, 502, 503, 504],
    allowed_methods=["GET", "POST", "DELETE"],
    raise_on_status=False,
)


class BinanceAPIError(Exception):
    """Raised when the Binance API returns an error payload."""

    def __init__(self, code: int, message: str):
        self.code = code
        self.message = message
        super().__init__(f"Binance API error {code}: {message}")


class BinanceClient:
    """
    Thin wrapper around the Binance Futures Testnet REST API.

    Args:
        api_key:    Testnet API key.
        api_secret: Testnet API secret.
        base_url:   Base URL (defaults to testnet).
        timeout:    HTTP timeout in seconds.
        recv_window: Milliseconds the request is valid for (default 5000).
    """

    def __init__(
        self,
        api_key: str,
        api_secret: str,
        base_url: str = TESTNET_BASE_URL,
        timeout: int = 10,
        recv_window: int = 5000,
    ):
        if not api_key or not api_secret:
            raise ValueError("api_key and api_secret must not be empty.")

        self._api_key = api_key
        self._api_secret = api_secret.encode()
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.recv_window = recv_window

        self._session = self._build_session()
        logger.info(
            "BinanceClient initialised | base_url=%s | recv_window=%d ms",
            self.base_url,
            self.recv_window,
        )

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _build_session(self) -> requests.Session:
        session = requests.Session()
        session.headers.update(
            {
                "X-MBX-APIKEY": self._api_key,
                "Content-Type": "application/x-www-form-urlencoded",
            }
        )
        adapter = HTTPAdapter(max_retries=_RETRY_STRATEGY)
        session.mount("https://", adapter)
        session.mount("http://", adapter)
        return session

    def _sign(self, params: dict) -> dict:
        """Append timestamp + HMAC-SHA256 signature to params dict."""
        params["timestamp"] = int(time.time() * 1000)
        params["recvWindow"] = self.recv_window
        query_string = urlencode(params)
        signature = hmac.new(
            self._api_secret, query_string.encode(), hashlib.sha256
        ).hexdigest()
        params["signature"] = signature
        return params

    def _handle_response(self, response: requests.Response) -> Any:
        """Parse response JSON; raise BinanceAPIError for API-level errors."""
        logger.debug(
            "HTTP %d | %s | body=%s",
            response.status_code,
            response.url,
            response.text[:500],
        )
        try:
            data = response.json()
        except ValueError:
            response.raise_for_status()
            return response.text

        # Binance wraps errors as {"code": <negative int>, "msg": "..."}
        if isinstance(data, dict) and "code" in data and data["code"] != 200:
            raise BinanceAPIError(data["code"], data.get("msg", "Unknown error"))

        # Also surface HTTP-level errors that came back as non-JSON
        response.raise_for_status()
        return data

    # ------------------------------------------------------------------
    # Public API methods
    # ------------------------------------------------------------------

    def get_server_time(self) -> int:
        """Return Binance server timestamp in ms (unauthenticated)."""
        url = f"{self.base_url}/fapi/v1/time"
        logger.debug("GET %s", url)
        resp = self._session.get(url, timeout=self.timeout)
        data = self._handle_response(resp)
        return data["serverTime"]

    def get_exchange_info(self) -> dict:
        """Fetch exchange info (symbols, filters, etc.)."""
        url = f"{self.base_url}/fapi/v1/exchangeInfo"
        logger.debug("GET %s", url)
        resp = self._session.get(url, timeout=self.timeout)
        return self._handle_response(resp)

    def get_account(self) -> dict:
        """Fetch account information (balances, positions)."""
        url = f"{self.base_url}/fapi/v2/account"
        params = self._sign({})
        logger.info("GET account | url=%s", url)
        resp = self._session.get(url, params=params, timeout=self.timeout)
        return self._handle_response(resp)

    def place_order(
        self,
        symbol: str,
        side: str,
        order_type: str,
        quantity: str,
        price: Optional[str] = None,
        stop_price: Optional[str] = None,
        time_in_force: str = "GTC",
        reduce_only: bool = False,
    ) -> dict:
        """
        Place a new order on Binance Futures Testnet.

        Args:
            symbol:        Trading pair, e.g. 'BTCUSDT'.
            side:          'BUY' or 'SELL'.
            order_type:    'MARKET', 'LIMIT', 'STOP_MARKET', 'STOP'.
            quantity:      Order quantity as a string (preserves precision).
            price:         Limit price (required for LIMIT / STOP).
            stop_price:    Stop trigger price (required for STOP / STOP_MARKET).
            time_in_force: 'GTC', 'IOC', 'FOK' (ignored for MARKET orders).
            reduce_only:   True to make the order reduce-only.

        Returns:
            Raw Binance order response dict.
        """
        url = f"{self.base_url}/fapi/v1/order"
        params: dict = {
            "symbol": symbol,
            "side": side,
            "type": order_type,
            "quantity": quantity,
        }

        if order_type in ("LIMIT", "STOP"):
            params["timeInForce"] = time_in_force
            if price:
                params["price"] = price

        if stop_price and order_type in ("STOP", "STOP_MARKET"):
            params["stopPrice"] = stop_price

        if reduce_only:
            params["reduceOnly"] = "true"

        # Log before signing (no secret in log)
        logger.info(
            "Placing order | symbol=%s side=%s type=%s qty=%s price=%s stopPrice=%s",
            symbol,
            side,
            order_type,
            quantity,
            price,
            stop_price,
        )

        signed_params = self._sign(params)

        try:
            resp = self._session.post(
                url,
                data=signed_params,
                timeout=self.timeout,
            )
            result = self._handle_response(resp)
            logger.info(
                "Order placed successfully | orderId=%s status=%s",
                result.get("orderId"),
                result.get("status"),
            )
            return result

        except BinanceAPIError:
            logger.exception("Binance API rejected the order")
            raise
        except requests.exceptions.ConnectionError as exc:
            logger.error("Network connection error: %s", exc)
            raise
        except requests.exceptions.Timeout as exc:
            logger.error("Request timed out: %s", exc)
            raise
        except requests.exceptions.RequestException as exc:
            logger.error("Unexpected HTTP error: %s", exc)
            raise

    def cancel_order(self, symbol: str, order_id: int) -> dict:
        """Cancel an open order by orderId."""
        url = f"{self.base_url}/fapi/v1/order"
        params = self._sign({"symbol": symbol, "orderId": order_id})
        logger.info("Cancelling order | symbol=%s orderId=%d", symbol, order_id)
        resp = self._session.delete(url, params=params, timeout=self.timeout)
        return self._handle_response(resp)

    def get_open_orders(self, symbol: Optional[str] = None) -> list:
        """Fetch all open orders, optionally filtered by symbol."""
        url = f"{self.base_url}/fapi/v1/openOrders"
        params: dict = {}
        if symbol:
            params["symbol"] = symbol
        params = self._sign(params)
        logger.info("Fetching open orders | symbol=%s", symbol or "ALL")
        resp = self._session.get(url, params=params, timeout=self.timeout)
        return self._handle_response(resp)

    def close(self):
        """Close the underlying HTTP session."""
        self._session.close()
        logger.debug("HTTP session closed.")

    def __enter__(self):
        return self

    def __exit__(self, *_):
        self.close()
