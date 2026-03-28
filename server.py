#!/usr/bin/env python3
"""
server.py – Flask REST API that wraps the trading bot for the web UI.

Endpoints
---------
GET  /api/status          – ping / account balance
GET  /api/orders          – open orders (optional ?symbol=)
POST /api/orders          – place a new order
DELETE /api/orders/<id>   – cancel an order
GET  /api/history         – recent order history (last 20 from server-side cache)
"""

from __future__ import annotations

import os
from decimal import Decimal
from functools import lru_cache
from typing import Optional

from flask import Flask, jsonify, request
from flask_cors import CORS

# Load .env if available
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

from bot.client import BinanceAPIError, BinanceClient
from bot.logging_config import setup_logging, get_logger
from bot.validators import validate_all, validate_symbol

# ── logging ────────────────────────────────────────────────────────────────
setup_logging("INFO")
logger = get_logger("server")

# ── Flask app ──────────────────────────────────────────────────────────────
app = Flask(__name__, static_folder="web", static_url_path="")
CORS(app)

# In-memory order history (last 50 orders this session)
_order_history: list[dict] = []


def _get_client() -> BinanceClient:
    api_key = os.environ.get("BINANCE_API_KEY", "").strip()
    api_secret = os.environ.get("BINANCE_API_SECRET", "").strip()
    if not api_key or not api_secret:
        raise ValueError("BINANCE_API_KEY and BINANCE_API_SECRET must be set.")
    return BinanceClient(api_key=api_key, api_secret=api_secret)


def _fmt(value: Optional[Decimal]) -> Optional[str]:
    if value is None:
        return None
    return format(value, "f").rstrip("0").rstrip(".")


def _err(msg: str, code: int = 400) -> tuple:
    logger.warning("API error %d: %s", code, msg)
    return jsonify({"ok": False, "error": msg}), code


# ── Routes ─────────────────────────────────────────────────────────────────

@app.route("/")
def index():
    return app.send_static_file("index.html")


@app.route("/api/status")
def status():
    """Return server connectivity + USDT balance."""
    try:
        with _get_client() as c:
            server_time = c.get_server_time()
            account = c.get_account()
    except ValueError as e:
        return _err(str(e), 401)
    except BinanceAPIError as e:
        return _err(str(e), 502)
    except Exception as e:
        return _err(f"Network error: {e}", 503)

    assets = account.get("assets", [])
    usdt = next((a for a in assets if a.get("asset") == "USDT"), {})

    return jsonify({
        "ok": True,
        "serverTime": server_time,
        "balance": {
            "walletBalance":    usdt.get("walletBalance", "0"),
            "availableBalance": usdt.get("availableBalance", "0"),
            "unrealizedProfit": usdt.get("unrealizedProfit", "0"),
        },
    })


@app.route("/api/orders", methods=["GET"])
def get_orders():
    """List open orders, optional ?symbol= filter."""
    symbol = request.args.get("symbol")
    if symbol:
        try:
            symbol = validate_symbol(symbol)
        except ValueError as e:
            return _err(str(e))

    try:
        with _get_client() as c:
            orders = c.get_open_orders(symbol=symbol)
    except ValueError as e:
        return _err(str(e), 401)
    except BinanceAPIError as e:
        return _err(str(e), 502)
    except Exception as e:
        return _err(f"Network error: {e}", 503)

    return jsonify({"ok": True, "orders": orders})


@app.route("/api/orders", methods=["POST"])
def place_order():
    """
    Place a new order.

    Body (JSON):
        symbol, side, type, quantity, price?, stopPrice?, timeInForce?, reduceOnly?
    """
    body = request.get_json(force=True, silent=True) or {}
    logger.info("POST /api/orders | body=%s", body)

    # --- validate ---
    try:
        validated = validate_all(
            symbol=body.get("symbol", ""),
            side=body.get("side", ""),
            order_type=body.get("type", ""),
            quantity=body.get("quantity", ""),
            price=body.get("price"),
            stop_price=body.get("stopPrice"),
        )
    except ValueError as e:
        return _err(str(e))

    tif = body.get("timeInForce", "GTC").upper()
    reduce_only = bool(body.get("reduceOnly", False))

    try:
        with _get_client() as c:
            result = c.place_order(
                symbol=validated["symbol"],
                side=validated["side"],
                order_type=validated["order_type"],
                quantity=_fmt(validated["quantity"]),
                price=_fmt(validated["price"]),
                stop_price=_fmt(validated["stop_price"]),
                time_in_force=tif,
                reduce_only=reduce_only,
            )
    except ValueError as e:
        return _err(str(e), 401)
    except BinanceAPIError as e:
        return _err(str(e), 502)
    except Exception as e:
        logger.exception("Unexpected error placing order")
        return _err(f"Unexpected error: {e}", 500)

    # cache to history
    _order_history.insert(0, result)
    if len(_order_history) > 50:
        _order_history.pop()

    return jsonify({"ok": True, "order": result}), 201


@app.route("/api/orders/<int:order_id>", methods=["DELETE"])
def cancel_order(order_id: int):
    """Cancel an order by ID. Requires ?symbol= query param."""
    symbol = request.args.get("symbol", "")
    try:
        symbol = validate_symbol(symbol)
    except ValueError as e:
        return _err(str(e))

    try:
        with _get_client() as c:
            result = c.cancel_order(symbol=symbol, order_id=order_id)
    except BinanceAPIError as e:
        return _err(str(e), 502)
    except Exception as e:
        return _err(f"Network error: {e}", 503)

    return jsonify({"ok": True, "order": result})


@app.route("/api/history")
def history():
    """Return in-session order history."""
    return jsonify({"ok": True, "orders": _order_history})


# ── Entry point ────────────────────────────────────────────────────────────

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    logger.info("Starting Flask server on port %d", port)
    print(f"\n  🚀  Trading Bot UI  →  http://localhost:{port}\n")
    app.run(host="0.0.0.0", port=port, debug=False)
