from __future__ import annotations

import argparse
import os
import sys
import textwrap

# Load .env file if python-dotenv is installed (optional convenience)
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

from bot.client import BinanceAPIError, BinanceClient
from bot.logging_config import setup_logging, get_logger
from bot.orders import place_order, print_order_response
from bot.validators import validate_all, validate_symbol

# ──────────────────────────────────────────────────────────────────────────────
# Helpers
# ──────────────────────────────────────────────────────────────────────────────

def _get_credentials() -> tuple[str, str]:
    """
    Read API credentials from environment variables.
    BINANCE_API_KEY and BINANCE_API_SECRET must be set (or in a .env file).
    """
    api_key = os.environ.get("BINANCE_API_KEY", "").strip()
    api_secret = os.environ.get("BINANCE_API_SECRET", "").strip()

    if not api_key or not api_secret:
        print(
            "\n❌  Missing credentials.\n"
            "    Set BINANCE_API_KEY and BINANCE_API_SECRET as environment variables,\n"
            "    or create a .env file in the project root.\n",
            file=sys.stderr,
        )
        sys.exit(1)

    return api_key, api_secret


def _banner():
    print(
        "\n"
        "  ╔══════════════════════════════════════════╗\n"
        "  ║   Binance Futures Testnet Trading Bot    ║\n"
        "  ╚══════════════════════════════════════════╝\n"
    )


# ──────────────────────────────────────────────────────────────────────────────
# Sub-command handlers
# ──────────────────────────────────────────────────────────────────────────────

def cmd_place(args: argparse.Namespace, client: BinanceClient, logger) -> None:
    """Handle the 'place' sub-command."""
    try:
        validated = validate_all(
            symbol=args.symbol,
            side=args.side,
            order_type=args.type,
            quantity=args.quantity,
            price=args.price,
            stop_price=args.stop_price,
        )
    except ValueError as exc:
        print(f"\n❌  Validation error: {exc}\n", file=sys.stderr)
        logger.error("Validation failed: %s", exc)
        sys.exit(2)

    try:
        place_order(
            client=client,
            symbol=validated["symbol"],
            side=validated["side"],
            order_type=validated["order_type"],
            quantity=validated["quantity"],
            price=validated["price"],
            stop_price=validated["stop_price"],
            time_in_force=args.time_in_force,
            reduce_only=args.reduce_only,
            dry_run=args.dry_run,
        )
    except BinanceAPIError as exc:
        print(f"\n❌  Exchange rejected the order: {exc}\n", file=sys.stderr)
        logger.error("BinanceAPIError during order placement: %s", exc)
        sys.exit(3)
    except Exception as exc:
        print(f"\n❌  Unexpected error: {exc}\n", file=sys.stderr)
        logger.exception("Unhandled exception during order placement")
        sys.exit(4)


def cmd_orders(args: argparse.Namespace, client: BinanceClient, logger) -> None:
    """Handle the 'orders' sub-command (list open orders)."""
    symbol = None
    if args.symbol:
        try:
            symbol = validate_symbol(args.symbol)
        except ValueError as exc:
            print(f"\n❌  {exc}\n", file=sys.stderr)
            sys.exit(2)

    try:
        open_orders = client.get_open_orders(symbol=symbol)
    except BinanceAPIError as exc:
        print(f"\n❌  {exc}\n", file=sys.stderr)
        sys.exit(3)

    if not open_orders:
        print(f"\n  No open orders{' for ' + symbol if symbol else ''}.\n")
        return

    width = 52
    print(f"\n  Open orders ({len(open_orders)} total):\n")
    for order in open_orders:
        print("  ┌" + "─" * width + "┐")
        for key in ("orderId", "symbol", "side", "type", "status",
                    "origQty", "executedQty", "price"):
            val = str(order.get(key, "N/A"))
            label = key[:18]
            print(f"  │  {label:<18}{val:<{width - 20}}│")
        print("  └" + "─" * width + "┘\n")


def cmd_cancel(args: argparse.Namespace, client: BinanceClient, logger) -> None:
    """Handle the 'cancel' sub-command."""
    try:
        symbol = validate_symbol(args.symbol)
    except ValueError as exc:
        print(f"\n❌  {exc}\n", file=sys.stderr)
        sys.exit(2)

    try:
        result = client.cancel_order(symbol=symbol, order_id=args.order_id)
    except BinanceAPIError as exc:
        print(f"\n❌  {exc}\n", file=sys.stderr)
        sys.exit(3)

    print_order_response(result)
    print(f"✅  Order {args.order_id} cancelled.\n")


def cmd_account(args: argparse.Namespace, client: BinanceClient, logger) -> None:
    """Handle the 'account' sub-command (print USDT balance)."""
    try:
        account = client.get_account()
    except BinanceAPIError as exc:
        print(f"\n❌  {exc}\n", file=sys.stderr)
        sys.exit(3)

    assets = account.get("assets", [])
    usdt = next((a for a in assets if a.get("asset") == "USDT"), None)

    width = 52
    print("\n┌" + "─" * width + "┐")
    print(f"│{'  ACCOUNT SUMMARY':^{width}}│")
    print("├" + "─" * width + "┤")
    if usdt:
        for label, key in [
            ("Wallet Balance",    "walletBalance"),
            ("Available Balance", "availableBalance"),
            ("Unrealised PnL",    "unrealizedProfit"),
        ]:
            val = usdt.get(key, "N/A")
            print(f"│  {label:<18}{str(val):<{width - 20}}│")
    else:
        print(f"│  {'No USDT asset found.':<{width}}│")
    print("└" + "─" * width + "┘\n")


# ──────────────────────────────────────────────────────────────────────────────
# Parser construction
# ──────────────────────────────────────────────────────────────────────────────

def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="python cli.py",
        description="Binance Futures Testnet trading bot CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=textwrap.dedent(
            """
            examples:
              python cli.py place --symbol BTCUSDT --side BUY  --type MARKET --quantity 0.001
              python cli.py place --symbol ETHUSDT --side SELL --type LIMIT  --quantity 0.01 --price 3500
              python cli.py place --symbol BTCUSDT --side BUY  --type STOP_MARKET --quantity 0.001 --stop-price 95000
              python cli.py orders --symbol BTCUSDT
              python cli.py cancel --symbol BTCUSDT --order-id 123456
              python cli.py account
            """
        ),
    )

    parser.add_argument(
        "--log-level",
        default="INFO",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        help="Logging verbosity (default: INFO)",
    )

    sub = parser.add_subparsers(dest="command", metavar="COMMAND")
    sub.required = True

    # ---- place ----
    p_place = sub.add_parser("place", help="Place a new order")
    p_place.add_argument("--symbol",   required=True, help="e.g. BTCUSDT")
    p_place.add_argument("--side",     required=True, choices=["BUY", "SELL"],
                         type=str.upper, help="BUY or SELL")
    p_place.add_argument("--type",     required=True,
                         choices=["MARKET", "LIMIT", "STOP_MARKET", "STOP"],
                         type=str.upper, dest="type", help="Order type")
    p_place.add_argument("--quantity", required=True, type=float, help="Order quantity")
    p_place.add_argument("--price",    type=float, default=None,
                         help="Limit price (required for LIMIT/STOP)")
    p_place.add_argument("--stop-price", type=float, default=None, dest="stop_price",
                         help="Stop trigger price (required for STOP/STOP_MARKET)")
    p_place.add_argument("--time-in-force", default="GTC",
                         choices=["GTC", "IOC", "FOK"], dest="time_in_force",
                         help="Time-in-force for LIMIT orders (default: GTC)")
    p_place.add_argument("--reduce-only", action="store_true", dest="reduce_only",
                         help="Mark order as reduce-only")
    p_place.add_argument("--dry-run", action="store_true", dest="dry_run",
                         help="Print order summary without sending to exchange")

    # ---- orders ----
    p_orders = sub.add_parser("orders", help="List open orders")
    p_orders.add_argument("--symbol", default=None, help="Filter by symbol")

    # ---- cancel ----
    p_cancel = sub.add_parser("cancel", help="Cancel an open order")
    p_cancel.add_argument("--symbol",   required=True, help="e.g. BTCUSDT")
    p_cancel.add_argument("--order-id", required=True, type=int, dest="order_id",
                          help="Order ID to cancel")

    # ---- account ----
    sub.add_parser("account", help="Show account balance summary")

    return parser


# ──────────────────────────────────────────────────────────────────────────────
# Entry point
# ──────────────────────────────────────────────────────────────────────────────

def main():
    parser = build_parser()
    args = parser.parse_args()

    logger = setup_logging(args.log_level)
    cli_logger = get_logger("cli")
    cli_logger.info("Command: %s | args: %s", args.command, vars(args))

    _banner()

    api_key, api_secret = _get_credentials()

    # Determine if this is a dry-run before creating client
    is_dry_run = getattr(args, "dry_run", False)

    with BinanceClient(api_key=api_key, api_secret=api_secret) as client:
        # Smoke-test connectivity (skipped in dry-run to allow offline testing)
        if not is_dry_run:
            try:
                server_time = client.get_server_time()
                cli_logger.info("Testnet server time: %d", server_time)
            except Exception as exc:
                print(
                    f"\n❌  Cannot reach Binance Testnet: {exc}\n"
                    "    Check your internet connection and try again.\n",
                    file=sys.stderr,
                )
                cli_logger.error("Testnet connectivity check failed: %s", exc)
                sys.exit(5)

        dispatch = {
            "place":   cmd_place,
            "orders":  cmd_orders,
            "cancel":  cmd_cancel,
            "account": cmd_account,
        }
        dispatch[args.command](args, client, cli_logger)


if __name__ == "__main__":
    main()
