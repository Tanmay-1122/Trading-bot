"""
High-level order placement logic.

Sits between the CLI layer and the raw BinanceClient.
Responsible for:
  - Formatting Decimal values into strings safe for the API
  - Printing a clean order summary and response to stdout
  - Delegating error handling back to the caller
"""

from __future__ import annotations

from decimal import Decimal
from typing import Optional

from .client import BinanceClient
from .logging_config import get_logger

logger = get_logger("orders")

# ──────────────────────────────────────────────────────────────────────────────
# Formatting helpers
# ──────────────────────────────────────────────────────────────────────────────

def _fmt(value: Optional[Decimal]) -> Optional[str]:
    """
    Convert a Decimal to a string without trailing zeros.
    Returns None if value is None (so callers can do simple truthiness checks).
    """
    if value is None:
        return None
    return format(value, "f").rstrip("0").rstrip(".")


def print_order_summary(
    symbol: str,
    side: str,
    order_type: str,
    quantity: Decimal,
    price: Optional[Decimal],
    stop_price: Optional[Decimal],
) -> None:
    """Print a human-readable summary of the order about to be sent."""
    width = 52
    print()
    print("┌" + "─" * width + "┐")
    print(f"│{'  ORDER REQUEST SUMMARY':^{width}}│")
    print("├" + "─" * width + "┤")
    print(f"│  {'Symbol':<18}{symbol:<{width - 20}}│")
    print(f"│  {'Side':<18}{side:<{width - 20}}│")
    print(f"│  {'Order Type':<18}{order_type:<{width - 20}}│")
    print(f"│  {'Quantity':<18}{_fmt(quantity):<{width - 20}}│")
    if price is not None:
        print(f"│  {'Price':<18}{_fmt(price):<{width - 20}}│")
    if stop_price is not None:
        print(f"│  {'Stop Price':<18}{_fmt(stop_price):<{width - 20}}│")
    print("└" + "─" * width + "┘")
    print()


def print_order_response(response: dict) -> None:
    """Print key fields from the Binance order response."""
    width = 52
    fields = [
        ("Order ID",      response.get("orderId", "N/A")),
        ("Symbol",        response.get("symbol", "N/A")),
        ("Side",          response.get("side", "N/A")),
        ("Type",          response.get("type", "N/A")),
        ("Status",        response.get("status", "N/A")),
        ("Orig Qty",      response.get("origQty", "N/A")),
        ("Executed Qty",  response.get("executedQty", "N/A")),
        ("Avg Price",     response.get("avgPrice") or response.get("price", "N/A")),
        ("Time in Force", response.get("timeInForce", "N/A")),
    ]

    print("┌" + "─" * width + "┐")
    print(f"│{'  ORDER RESPONSE':^{width}}│")
    print("├" + "─" * width + "┤")
    for label, value in fields:
        print(f"│  {label:<18}{str(value):<{width - 20}}│")
    print("└" + "─" * width + "┘")
    print()


# ──────────────────────────────────────────────────────────────────────────────
# Core order function
# ──────────────────────────────────────────────────────────────────────────────

def place_order(
    client: BinanceClient,
    symbol: str,
    side: str,
    order_type: str,
    quantity: Decimal,
    price: Optional[Decimal] = None,
    stop_price: Optional[Decimal] = None,
    time_in_force: str = "GTC",
    reduce_only: bool = False,
    dry_run: bool = False,
) -> Optional[dict]:
    """
    Validate, summarise, and place a futures order.

    Args:
        client:         Initialised BinanceClient.
        symbol:         Trading pair (already validated).
        side:           'BUY' or 'SELL' (already validated).
        order_type:     'MARKET', 'LIMIT', 'STOP_MARKET', 'STOP'.
        quantity:       Validated Decimal quantity.
        price:          Validated Decimal price (or None for MARKET).
        stop_price:     Validated Decimal stop price (or None).
        time_in_force:  GTC / IOC / FOK for LIMIT orders.
        reduce_only:    Whether to set reduceOnly flag.
        dry_run:        If True, print summary but skip the actual API call.

    Returns:
        Binance response dict, or None on dry-run.
    """
    print_order_summary(symbol, side, order_type, quantity, price, stop_price)

    if dry_run:
        print("⚠️  DRY-RUN mode – order NOT sent to exchange.\n")
        logger.info("Dry-run order | symbol=%s side=%s type=%s qty=%s",
                    symbol, side, order_type, _fmt(quantity))
        return None

    response = client.place_order(
        symbol=symbol,
        side=side,
        order_type=order_type,
        quantity=_fmt(quantity),         # type: ignore[arg-type]
        price=_fmt(price),
        stop_price=_fmt(stop_price),
        time_in_force=time_in_force,
        reduce_only=reduce_only,
    )

    print_order_response(response)

    status = response.get("status", "UNKNOWN")
    if status in ("NEW", "PARTIALLY_FILLED", "FILLED"):
        print(f"✅  Order accepted by exchange. Status: {status}\n")
        logger.info(
            "Order success | orderId=%s status=%s executedQty=%s",
            response.get("orderId"),
            status,
            response.get("executedQty"),
        )
    else:
        print(f"⚠️  Unexpected order status: {status}\n")
        logger.warning("Unexpected status in order response: %s", response)

    return response
