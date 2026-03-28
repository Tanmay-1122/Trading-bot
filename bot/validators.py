"""
Input validation for CLI parameters before they reach the API layer.
All validators raise ValueError with a human-readable message on failure.
"""

from __future__ import annotations

from decimal import Decimal, InvalidOperation
from typing import Optional

from .logging_config import get_logger

logger = get_logger("validators")

# Supported values
VALID_SIDES = {"BUY", "SELL"}
VALID_ORDER_TYPES = {"MARKET", "LIMIT", "STOP_MARKET", "STOP"}

# Loose symbol sanity-check (Binance futures pairs are 2-10 uppercase letters)
MIN_SYMBOL_LEN = 4
MAX_SYMBOL_LEN = 20


def validate_symbol(symbol: str) -> str:
    """
    Normalise and validate a trading symbol.

    >>> validate_symbol("btcusdt")
    'BTCUSDT'
    """
    cleaned = symbol.strip().upper()
    if not cleaned.isalpha():
        raise ValueError(
            f"Symbol '{symbol}' contains non-alphabetic characters. "
            "Expected something like BTCUSDT."
        )
    if not (MIN_SYMBOL_LEN <= len(cleaned) <= MAX_SYMBOL_LEN):
        raise ValueError(
            f"Symbol '{symbol}' length {len(cleaned)} is outside the expected "
            f"range [{MIN_SYMBOL_LEN}, {MAX_SYMBOL_LEN}]."
        )
    logger.debug("Symbol validated: %s", cleaned)
    return cleaned


def validate_side(side: str) -> str:
    """
    Validate order side (BUY / SELL).

    >>> validate_side("buy")
    'BUY'
    """
    cleaned = side.strip().upper()
    if cleaned not in VALID_SIDES:
        raise ValueError(
            f"Invalid side '{side}'. Must be one of: {', '.join(sorted(VALID_SIDES))}."
        )
    logger.debug("Side validated: %s", cleaned)
    return cleaned


def validate_order_type(order_type: str) -> str:
    """
    Validate order type (MARKET / LIMIT / STOP_MARKET / STOP).

    >>> validate_order_type("limit")
    'LIMIT'
    """
    cleaned = order_type.strip().upper().replace("-", "_")
    if cleaned not in VALID_ORDER_TYPES:
        raise ValueError(
            f"Invalid order type '{order_type}'. "
            f"Must be one of: {', '.join(sorted(VALID_ORDER_TYPES))}."
        )
    logger.debug("Order type validated: %s", cleaned)
    return cleaned


def validate_quantity(quantity: str | float) -> Decimal:
    """
    Validate that quantity is a positive finite number.

    Returns a Decimal for precision-safe downstream use.
    """
    try:
        qty = Decimal(str(quantity))
    except InvalidOperation:
        raise ValueError(f"Quantity '{quantity}' is not a valid number.")

    if qty <= 0:
        raise ValueError(f"Quantity must be positive, got {qty}.")

    logger.debug("Quantity validated: %s", qty)
    return qty


def validate_price(price: str | float | None, order_type: str) -> Optional[Decimal]:
    """
    Validate price based on order type.

    - LIMIT / STOP orders  → price is required and must be positive.
    - MARKET / STOP_MARKET → price must be None (ignored).
    """
    requires_price = order_type in {"LIMIT", "STOP"}

    if requires_price:
        if price is None:
            raise ValueError(
                f"Price is required for {order_type} orders but was not provided."
            )
        try:
            p = Decimal(str(price))
        except InvalidOperation:
            raise ValueError(f"Price '{price}' is not a valid number.")
        if p <= 0:
            raise ValueError(f"Price must be positive, got {p}.")
        logger.debug("Price validated: %s", p)
        return p

    else:
        if price is not None:
            logger.warning(
                "Price '%s' supplied for %s order — it will be ignored.",
                price,
                order_type,
            )
        return None


def validate_stop_price(
    stop_price: str | float | None, order_type: str
) -> Optional[Decimal]:
    """
    Validate stop price for STOP / STOP_MARKET orders.
    """
    needs_stop = order_type in {"STOP", "STOP_MARKET"}

    if needs_stop:
        if stop_price is None:
            raise ValueError(
                f"--stop-price is required for {order_type} orders."
            )
        try:
            sp = Decimal(str(stop_price))
        except InvalidOperation:
            raise ValueError(f"Stop price '{stop_price}' is not a valid number.")
        if sp <= 0:
            raise ValueError(f"Stop price must be positive, got {sp}.")
        logger.debug("Stop price validated: %s", sp)
        return sp

    return None


def validate_all(
    symbol: str,
    side: str,
    order_type: str,
    quantity: str | float,
    price: Optional[str | float] = None,
    stop_price: Optional[str | float] = None,
) -> dict:
    """
    Run all validations in one call and return a clean parameter dict.

    Raises ValueError with a descriptive message on the first failure.
    """
    validated_type = validate_order_type(order_type)
    return {
        "symbol": validate_symbol(symbol),
        "side": validate_side(side),
        "order_type": validated_type,
        "quantity": validate_quantity(quantity),
        "price": validate_price(price, validated_type),
        "stop_price": validate_stop_price(stop_price, validated_type),
    }
