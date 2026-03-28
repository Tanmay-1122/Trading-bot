# Quick Start Guide

Get the Binance Futures Trading Bot running in **5 minutes**.

## Prerequisites

- **Python 3.9+** ([Download](https://www.python.org/downloads/))
- **Git** ([Download](https://git-scm.com/))
- **Binance Testnet Account** ([Sign up free](https://testnet.binancefuture.com))

---

## Step 1: Get API Keys (2 min)

1. Go to [https://testnet.binancefuture.com](https://testnet.binancefuture.com)
2. Log in with GitHub/Google
3. Click **API Key** in the top menu
4. Click **Generate Key**
5. Copy your **API Key** and **Secret Key**

---

## Step 2: Clone & Setup (2 min)

```bash
# Clone the repository
git clone https://github.com/YOUR_USERNAME/binance-futures-trading-bot.git
cd binance-futures-trading-bot

# Create virtual environment
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

---

## Step 3: Configure (1 min)

```bash
# Copy environment template
cp .env.example .env

# Edit .env and paste your API keys
# On Windows: notepad .env
# On Mac/Linux: nano .env
# Change:
#   BINANCE_API_KEY=your_key_here
#   BINANCE_API_SECRET=your_secret_here
```

---

## Step 4: Run (Start Now!)

### Option A: Web Dashboard

```bash
python server.py
```

Then open **http://localhost:5000** in your browser.

**Features**:
- Live price chart with TradingView
- Place orders via form
- View open orders
- See activity feed
- Auto-refresh balance

### Option B: CLI Tool

```bash
# Place a market order
python cli.py place --symbol BTCUSDT --side BUY --type MARKET --quantity 0.001

# View open orders
python cli.py orders

# View balance
python cli.py account

# Cancel an order
python cli.py cancel --symbol BTCUSDT --order-id 12345678

# Test without executing (dry-run)
python cli.py place --symbol BTCUSDT --side BUY --type MARKET --quantity 0.001 --dry-run
```

---

## Common Commands

### Web Dashboard
```bash
python server.py
# Open: http://localhost:5000
```

### Place a Buy Order
```bash
python cli.py place --symbol BTCUSDT --side BUY --type MARKET --quantity 0.001
```

### Place a Sell Order
```bash
python cli.py place --symbol ETHUSDT --side SELL --type MARKET --quantity 0.01
```

### Check Orders
```bash
python cli.py orders --symbol BTCUSDT
```

### Cancel an Order
```bash
python cli.py cancel --symbol BTCUSDT --order-id 3847291056
```

### Check Balance
```bash
python cli.py account
```

---

## Troubleshooting

### "Missing credentials"
→ Check `.env` file has your API keys (no spaces, correct format)

### "Connection error"
→ Verify internet connection and Binance testnet is accessible

### "Invalid symbol"
→ Use format like `BTCUSDT`, not `BTC` (check [testnet symbols](https://testnet.binancefuture.com))

### "Testnet balance is 0"
→ Go to [testnet.binancefuture.com](https://testnet.binancefuture.com) and deposit test funds

### Port 5000 already in use
```bash
# Run on different port
PORT=8000 python server.py
# Open: http://localhost:8000
```

---

## Next Steps

- 📖 **Read the full [README.md](README.md)** for detailed features
- 🚀 **See [DEPLOYMENT.md](DEPLOYMENT.md)** for production setup
- 🔒 **Review [SECURITY.md](SECURITY.md)** for best practices
- 🤝 **Check [CONTRIBUTING.md](CONTRIBUTING.md)** to contribute
- 📞 **Open an [Issue](../../issues)** for questions

---

## Common Questions

**Q: Can I use mainnet?**  
A: This is testnet-only by default. For mainnet, see [SECURITY.md](SECURITY.md).

**Q: Can I automate trading?**  
A: Currently manual execution. Extend the code to add strategies.

**Q: What orders types are supported?**  
A: MARKET, LIMIT, STOP, STOP_MARKET, with BUY/SELL sides.

**Q: Is this production-ready?**  
A: For testnet, yes! See [DEPLOYMENT.md](DEPLOYMENT.md) for production.

**Q: How do I report bugs?**  
A: Open a GitHub [issue](../../issues) with details.

---

## Example Workflow

```bash
# 1. Start the dashboard
python server.py

# 2. In another terminal, check balance
python cli.py account

# 3. Test a dry-run order
python cli.py place --symbol BTCUSDT --side BUY --type MARKET --quantity 0.001 --dry-run

# 4. Place a real order
python cli.py place --symbol BTCUSDT --side BUY --type MARKET --quantity 0.001

# 5. Check open orders
python cli.py orders

# 6. View the order in dashboard (http://localhost:5000)
# 7. Cancel if needed
python cli.py cancel --symbol BTCUSDT --order-id <ORDER_ID>
```

---

## Need Help?

- 📚 See detailed docs in [README.md](README.md)
- 🚀 For deployment, see [DEPLOYMENT.md](DEPLOYMENT.md)
- 🔒 For security, see [SECURITY.md](SECURITY.md)
- 🤝 To contribute, see [CONTRIBUTING.md](CONTRIBUTING.md)
- 💬 Open a [GitHub Discussion](../../discussions)
- 🐛 Report bugs on [GitHub Issues](../../issues)

---

**Happy Trading!** 🚀

For more info: [https://github.com/YOUR_USERNAME/binance-futures-trading-bot](https://github.com/YOUR_USERNAME/binance-futures-trading-bot)
