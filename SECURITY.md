# Security Policy

## Reporting Security Vulnerabilities

**Do not publicly disclose security vulnerabilities.** Instead, please report them responsibly to the maintainers.

### How to Report

1. **Email**: Send a detailed report to [your-security-email@example.com] (or open a private security advisory)
2. **GitHub Security Advisory**: Use the "Report a vulnerability" button on the Security tab
3. **Include**:
   - Description of the vulnerability
   - Steps to reproduce
   - Potential impact
   - Suggested fix (if any)

We will:
- Acknowledge receipt within 48 hours
- Investigate and provide updates
- Release a patch within a reasonable timeframe
- Credit you in the security advisory (unless you prefer anonymity)

---

## Security Practices

### ✅ What We Do
- **HMAC-SHA256 Signing** – All Binance API requests are cryptographically signed
- **Timestamp Validation** – 5-second request window to prevent replay attacks
- **No Secrets in Code** – Credentials stored in `.env` file (not in repository)
- **Secure Session** – Connection pooling with SSL/TLS verification
- **Input Validation** – All user inputs validated before API calls
- **Error Handling** – Sensitive information not leaked in error messages
- **Dependency Updates** – Regular updates to security patches

### ⚠️ Known Limitations
- **Testnet Only** – This bot is designed for Binance Futures Testnet
- **No Rate Limiting** – You must implement rate limiting for production use
- **No IP Whitelisting** – Configure Binance IP restrictions manually
- **No API Level Restrictions** – Set up API key restrictions on Binance directly
- **No 2FA** – Binance 2FA must be enabled at account level

---

## Recommendations for Safe Use

### Before Using in Production

1. **Create a Dedicated API Key**
   - Log into Binance
   - Generate an API key with following restrictions:
     - ✅ Futures Trading Only (restrict to /fapi/v1/order endpoints)
     - ✅ IP Whitelist (restrict to your server IP)
     - ❌ Disable Withdrawal

2. **Use Environment Variables**
   ```bash
   export BINANCE_API_KEY="your_key"
   export BINANCE_API_SECRET="your_secret"
   ```
   Never hardcode credentials in code.

3. **Monitor Logs**
   - Review `logs/trading_bot.log` regularly
   - Set up alerts for failed API calls
   - Watch for unauthorized order attempts

4. **Network Security**
   - Run on a private VPC if possible
   - Use firewall rules to restrict access
   - Enable HTTPS if exposing the web UI (use reverse proxy like nginx)

5. **Backup & Recovery**
   - Store API keys in a password manager
   - Document your setup
   - Test recovery procedures

### General Best Practices

- **Never share your `.env` file** – Even with team members; use separate API keys
- **Rotate API keys periodically** – Every 3-6 months
- **Use environment-specific keys** – Separate testnet and mainnet keys
- **Audit trade history** – Regularly review order logs for anomalies
- **Test thoroughly on testnet** – Before running on mainnet
- **Keep dependencies updated** – `pip install --upgrade -r requirements.txt`
- **Use version control** – But never commit `.env`

---

## Potential Risks & Mitigations

| Risk | Mitigation |
|---|---|
| API key compromise | Use IP whitelisting + API key restrictions on Binance |
| Man-in-the-middle attack | HMAC signing + TLS verification (already implemented) |
| Unexpected large orders | Test with small amounts; use `--dry-run` mode first |
| Network outage | Retry logic handles transient failures; monitor logs |
| Code injection | Input validation on all user inputs |
| Unauthorized access | Firewall rules + authentication layer (if needed) |

---

## Security Updates

- Critical vulnerabilities: Patch released within 24 hours
- High priority: Patch released within 1 week
- Medium priority: Included in next release
- Low priority: Included in feature release

Subscribe to GitHub releases for notifications.

---

## Compliance

This project does NOT provide:
- ❌ Financial, investment, or legal advice
- ❌ Guaranteed profitability
- ❌ Regulatory compliance for your jurisdiction
- ❌ Protection against exchange API changes

Users are responsible for:
- ✅ Understanding their local regulations
- ✅ Risk management and position sizing
- ✅ Monitoring their accounts
- ✅ Backing up their configuration

---

## Contact

For security issues or clarifications, please contact the maintainers privately.

**Last Updated**: March 2025
