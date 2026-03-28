# 🚀 Binance Futures Trading Bot

> **Production-ready Python trading bot** for Binance Futures with REST API support, web UI dashboard, and CLI interface.

![Python 3.9+](https://img.shields.io/badge/python-3.9%2B-blue)
![Flask](https://img.shields.io/badge/framework-Flask-green)
![License](https://img.shields.io/badge/license-MIT-purple)

<div align="center">

**[Features](#-features)** • **[Quick Start](#-quick-start)** • **[Architecture](#-architecture)** • **[API Reference](#-api-reference)** • **[Deployment](#-deployment)**

</div>

---

## ✨ Features

| Feature | Details |
|---|---|
| **Order Types** | MARKET, LIMIT, STOP_MARKET, STOP (Stop-Limit) |
| **Interfaces** | Web Dashboard + CLI + REST API |
| **Real-time Charts** | TradingView embedded candlestick charts |
| **Validation** | Symbol, side, type, qty, price, stop-price — all validated pre-API |
| **Logging** | Rotating file log + console output + activity feed |
| **Error Handling** | API errors, network failures, invalid input — all clear & actionable |
| **Dry-run Mode** | Test orders without executing |
| **Session History** | Last 50 orders cached in-memory |
| **Auto-refresh** | Balance every 30s, orders every 15s |
| **Architecture** | Layered: `client.py` → `orders.py` → `cli.py` |
| **Production Ready** | HMAC-SHA256 signing, retry logic, connection pooling, CORS headers |

---

## Project Structure

```
trading_bot/
├── bot/
│   ├── __init__.py
│   ├── client.py          # Binance REST client (HMAC signing, retry, error handling)
│   ├── orders.py          # Order placement logic + stdout formatting
│   ├── validators.py      # Pure input validation (no I/O side effects)
│   └── logging_config.py  # Rotating file + console log setup
├── cli.py                 # CLI entry point (argparse sub-commands)
├── logs/
│   ├── market_order.log   # Sample MARKET order log
│   └── limit_order.log    # Sample LIMIT order log
├── .env.example           # Environment variable template
├── requirements.txt
└── README.md
```

---

## Setup

### 1. Clone / unzip and enter the directory

```bash
cd trading_bot
```

### 2. Create and activate a virtual environment

```bash
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Get Binance Futures Testnet credentials

1. Go to [https://testnet.binancefuture.com](https://testnet.binancefuture.com)
2. Log in with your GitHub or Google account
3. Navigate to **API Key** in the top menu → click **Generate Key**
4. Copy your **API Key** and **Secret Key**

### 5. Set environment variables

**Option A – `.env` file (recommended)**

```bash
cp .env.example .env
# Edit .env and paste your keys:
#   BINANCE_API_KEY=your_api_key_here
#   BINANCE_API_SECRET=your_api_secret_here
```

**Option B – Export directly in your shell**

```bash
export BINANCE_API_KEY="your_api_key_here"
export BINANCE_API_SECRET="your_api_secret_here"
```

---

## How to Run

### Place a MARKET order

```bash
# BUY 0.001 BTC at market price
python cli.py place --symbol BTCUSDT --side BUY --type MARKET --quantity 0.001

# SELL 0.01 ETH at market price
python cli.py place --symbol ETHUSDT --side SELL --type MARKET --quantity 0.01
```

### Place a LIMIT order

```bash
# BUY 0.001 BTC with a limit price of 90000 USDT
python cli.py place --symbol BTCUSDT --side BUY --type LIMIT --quantity 0.001 --price 90000

# SELL 0.05 ETH at 3450 USDT (GTC)
python cli.py place --symbol ETHUSDT --side SELL --type LIMIT --quantity 0.05 --price 3450

# Same sell, but IOC (immediate or cancel)
python cli.py place --symbol ETHUSDT --side SELL --type LIMIT --quantity 0.05 --price 3450 --time-in-force IOC
```

### Place a Stop-Market order (Bonus)

```bash
# Stop-market BUY triggers at 95000 USDT (e.g., breakout entry)
python cli.py place --symbol BTCUSDT --side BUY --type STOP_MARKET --quantity 0.001 --stop-price 95000
```

### Place a Stop-Limit order (Bonus)

```bash
# Stop-Limit SELL: triggers at 89000, places limit at 88000
python cli.py place --symbol BTCUSDT --side SELL --type STOP --quantity 0.001 \
    --stop-price 89000 --price 88000
```

### Dry-run (preview without sending)

```bash
python cli.py place --symbol BTCUSDT --side BUY --type MARKET --quantity 0.001 --dry-run
```

### View open orders

```bash
python cli.py orders                    # all symbols
python cli.py orders --symbol BTCUSDT  # filtered
```

### Cancel an order

```bash
python cli.py cancel --symbol BTCUSDT --order-id 3847291056
```

### View account balance

```bash
python cli.py account
```

---

## 📊 Web Dashboard

Run the Flask server to access the **web-based trading dashboard**:

```bash
python server.py
```

Then open **http://localhost:5000** in your browser.

### Dashboard Features
- **Live Price Chart** – TradingView candlestick chart with symbol switcher
- **Open Orders Table** – Real-time view; cancel orders directly
- **Session History** – All orders placed in the current session
- **Activity Feed** – Timestamps, status updates, and order confirmations
- **Balance Display** – Wallet balance, available balance, unrealized P&L
- **Order Form** – Place MARKET, LIMIT, STOP, and STOP_MARKET orders
- **Auto-refresh** – Balances update every 30s, orders every 15s

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────┐
│        User Interface                   │
│  (Web UI + CLI + REST API)              │
└────────────────┬────────────────────────┘
                 │
    ┌────────────▼──────────────┐
    │   Validators              │
    │   (validate inputs)       │
    └────────────┬──────────────┘
                 │
    ┌────────────▼──────────────┐
    │   Orders / CLI            │
    │  (format & orchestrate)   │
    └────────────┬──────────────┘
                 │
    ┌────────────▼──────────────┐
    │  BinanceClient            │
    │  (REST API + security)    │
    └────────────┬──────────────┘
                 │
    ┌────────────▼──────────────┐
    │  Binance Testnet API      │
    │ (HMAC-signed requests)    │
    └───────────────────────────┘
```

### Layer Descriptions

1. **BinanceClient** (`bot/client.py`)
   - Low-level REST wrapper
   - HMAC-SHA256 signing + timestamping
   - Retry logic (3 attempts on 5xx / network errors)
   - Connection pooling + persistent session
   - Transforms HTTP errors to `BinanceAPIError`

2. **Validators** (`bot/validators.py`)
   - Pure validation logic (no I/O)
   - Returns `Decimal` for precision
   - Default error messages for all validations

3. **Orders** (`bot/orders.py`)
   - Formats `Decimal` objects for the API
   - Prints human-readable order summaries
   - Orchestrates `BinanceClient` calls
   - Logging of order outcomes

4. **CLI** (`cli.py`)
   - Entry point for command-line users
   - Argparse sub-commands: `place`, `orders`, `cancel`, `account`
   - Credential loading + help text
   - Exit codes: 0 (success), 1 (credentials), 2 (validation), 3 (API), 4+ (other)

5. **Flask Server** (`server.py`)
   - REST API endpoints
   - CORS headers for cross-origin requests
   - In-memory session order history
   - Serves static web UI

---

## 🔄 API Reference

### REST Endpoints

#### **GET /api/status**
Returns server connectivity and account balance.

```bash
curl http://localhost:5000/api/status
```

Response:
```json
{
  "ok": true,
  "serverTime": 1689340324000,
  "balance": {
    "walletBalance": "1000.25",
    "availableBalance": "950.00",
    "unrealizedProfit": "50.25"
  }
}
```

#### **GET /api/orders**
Fetch open orders (optional symbol filter).

```bash
curl "http://localhost:5000/api/orders?symbol=BTCUSDT"
```

Response:
```json
{
  "ok": true,
  "orders": [
    {
      "orderId": 3847291056,
      "symbol": "BTCUSDT",
      "side": "BUY",
      "type": "LIMIT",
      "origQty": "0.001",
      "price": "90000",
      "status": "NEW"
    }
  ]
}
```

#### **POST /api/orders**
Place a new order.

```bash
curl -X POST http://localhost:5000/api/orders \
  -H "Content-Type: application/json" \
  -d '{
    "symbol": "BTCUSDT",
    "side": "BUY",
    "type": "MARKET",
    "quantity": "0.001"
  }'
```

#### **DELETE /api/orders/{orderId}**
Cancel an order by ID.

```bash
curl -X DELETE "http://localhost:5000/api/orders/3847291056?symbol=BTCUSDT"
```

#### **GET /api/history**
Fetch in-session order history (last 50).

```bash
curl http://localhost:5000/api/history
```

---

## 📦 Dependencies

| Package | Version | Purpose |
|---|---|---|
| `requests` | ≥2.31.0 | HTTP client |
| `urllib3` | ≥2.0.0 | HTTP retry + pooling |
| `python-dotenv` | ≥1.0.0 | .env file loading |
| `flask` | ≥3.0.0 | Web server + REST API |
| `flask-cors` | ≥4.0.0 | Cross-origin headers |

---

## 🚀 Deployment

### Local Development

```bash
python server.py          # Starts on http://localhost:5000
python cli.py --help      # View CLI options
```

### Docker (Optional)

Create a `Dockerfile`:

```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
ENV BINANCE_API_KEY=""
ENV BINANCE_API_SECRET=""
ENV PORT=5000
EXPOSE 5000
CMD ["python", "server.py"]
```

Build and run:

```bash
docker build -t trading-bot .
docker run -e BINANCE_API_KEY=xxx -e BINANCE_API_SECRET=yyy -p 5000:5000 trading-bot
```

### Production Server (Gunicorn)

```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 server:app
```

### Environment Variables

| Variable | Required | Example |
|---|---|---|
| `BINANCE_API_KEY` | ✅ | `xxxxxxxxxxxxxxxx` |
| `BINANCE_API_SECRET` | ✅ | `yyyyyyyyyyyyyyyy` |
| `PORT` | ❌ | `5000` (default) |
| `LOG_LEVEL` | ❌ | `INFO` (default) |

---

## 📝 Logging

Log files are stored in `logs/trading_bot.log` with rotating backups:
- **Max file size**: 5 MB
- **Backups**: 3 files
- **Format**: `TIMESTAMP | LEVEL | MODULE | MESSAGE`

Supported log levels (via environment or CLI):
- `DEBUG` – Verbose output (all HTTP requests + responses)
- `INFO` – Standard operation (trades, balance updates)
- `WARNING` – Issues that don't stop execution
- `ERROR` – Issues that stop execution

---

## 🛡️ Security

- ✅ **HMAC-SHA256 signing** – Every request to Binance is cryptographically signed
- ✅ **Timestamp validation** – 5-second window to prevent replay attacks
- ✅ **No hardcoding** – Credentials stored in `.env` (never in code)
- ✅ **CORS on localhost** – Web UI is protected by default (`0.0.0.0` in dev)
- ⚠️ **Testnet only** – Do not use mainnet keys; always verify credentials before production

---

## 💡 Testing

### Dry-run Orders

Test order logic without sending to Binance:

```bash
python cli.py place --symbol BTCUSDT --side BUY --type MARKET --quantity 0.001 --dry-run
```

Output: Prints order summary **without** making API call.

### Manual Testing Flow

1. **Fetch balance**: `python cli.py account`
2. **Dry-run order**: `python cli.py place ... --dry-run`
3. **Place live order**: `python cli.py place ...`
4. **Check open orders**: `python cli.py orders`
5. **Cancel order**: `python cli.py cancel --symbol BTCUSDT --order-id <ID>`

---

## ❓ FAQ

**Q: Can I use this on mainnet?**  
A: This bot targets **testnet only**. To use mainnet, change `TESTNET_BASE_URL` in `bot/client.py` and **use mainnet API keys**. **Do this at your own risk.**

**Q: What if I run out of testnet balance?**  
A: Visit [https://testnet.binancefuture.com](https://testnet.binancefuture.com), click Wallet → Deposit in the UI.

**Q: Can the bot auto-trade?**  
A: Currently, the bot is a **manual execution tool** with a web/CLI interface. Extend the code to add automated strategies by subclassing `BinanceClient`.

**Q: Does it support other exchanges?**  
A: Not yet. Contributions are welcome!

---

## 🤝 Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/my-feature`)
3. Commit your changes (`git commit -m 'Add my feature'`)
4. Push to the branch (`git push origin feature/my-feature`)
5. Open a Pull Request

See [CONTRIBUTING.md](CONTRIBUTING.md) for more details.

---

## 📄 License

This project is licensed under the **MIT License** — see [LICENSE](LICENSE) for details.

---

## 🙏 Acknowledgments

- **Binance** – Comprehensive Futures API documentation
- **TradingView** – Real-time charting widget
- **Python Community** – Requests, Flask, and related libraries

---

## 📞 Support

- **Issues**: Open a GitHub issue for bugs or feature requests
- **Discussions**: Use GitHub Discussions for general questions
- **Email**: For security concerns, please email privately

---

<div align="center">

**Made with ❤️ for the trading community**

⭐ If you found this helpful, please consider leaving a star!

</div>
|---|---|
| `requests` | HTTP client with connection pooling and retry |
| `urllib3` | Retry adapter for transient 5xx errors |
| `python-dotenv` | Optional `.env` file loading |

No third-party Binance SDK is used — all API interactions are raw authenticated REST calls.
