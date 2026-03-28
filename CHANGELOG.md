# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2025-03-28

### Added
- ✨ **Web Dashboard** – Modern terminal-style trading UI with TradingView charts
- 🔧 **REST API Server** – Flask-based API for order placement and balance queries
- 💻 **CLI Interface** – Command-line tool for automated trading
- 📊 **Real-time Charts** – Embedded TradingView candlestick with symbol switcher
- 🎯 **Order Types** – Support for MARKET, LIMIT, STOP_MARKET, and STOP orders
- ✅ **Input Validation** – Comprehensive validation before API calls
- 📝 **Logging** – Rotating file logs with configurable levels
- 🔐 **Security** – HMAC-SHA256 signing, retry logic, connection pooling
- 📋 **Session History** – Track last 50 orders in-memory
- 🔄 **Auto-refresh** – Balance every 30s, orders every 15s
- 📦 **Docker Support** – Dockerfile for containerized deployment
- 📚 **Documentation** – Comprehensive README with examples

### Initial Release
- Full Binance Futures Testnet integration
- Error handling for API failures and network issues
- Dry-run mode for testing orders without executing
- Activity feed with real-time order confirmations
- Support for reduce-only orders
- Time-in-force options (GTC, IOC, FOK)

---

## [Future Releases]

### Planned Features
- [ ] Automated trading strategies
- [ ] Order history persistence (database)
- [ ] Portfolio analysis and P&L tracking
- [ ] Multiple exchange support
- [ ] WebSocket for real-time updates
- [ ] Advanced charting indicators
- [ ] Risk management tools (stop-loss automation)
- [ ] API key rotation and security improvements
- [ ] Mobile-responsive dashboard
- [ ] Order templates and quick-buy buttons

### Under Investigation
- Grid trading strategy templates
- Price alert notifications
- Multi-account support
- Paper trading mode
- Backtesting framework

---

## How to Report Bugs

If you find a bug, please report it on the [GitHub Issues](https://github.com/yourrepo/issues) page with:
- Detailed description of the issue
- Steps to reproduce
- Expected vs. actual behavior
- Python version and OS
- Any relevant logs

---

## How to Request Features

Visit [GitHub Issues](https://github.com/yourrepo/issues) and open a new issue with:
- Title: `[FEATURE REQUEST] <description>`
- Use case and benefit
- Code examples if applicable

---

For more information, see [CONTRIBUTING.md](CONTRIBUTING.md).
