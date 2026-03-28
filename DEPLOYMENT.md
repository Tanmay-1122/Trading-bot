# Deployment Guide

Complete guide for deploying the Binance Futures Trading Bot to production.

## Table of Contents

1. [Local Development](#local-development)
2. [Docker Deployment](#docker-deployment)
3. [Cloud Deployment](#cloud-deployment)
4. [Production Checklist](#production-checklist)
5. [Monitoring & Maintenance](#monitoring--maintenance)

---

## Local Development

### Quick Start

```bash
# Clone repository
git clone https://github.com/your-username/binance-futures-trading-bot.git
cd binance-futures-trading-bot

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env and add your testnet API keys

# Run Flask server
python server.py
# Access at http://localhost:5000
```

### Testing the CLI

```bash
# Dry-run test (no actual order)
python cli.py place --symbol BTCUSDT --side BUY --type MARKET --quantity 0.001 --dry-run

# View open orders
python cli.py orders

# View account balance
python cli.py account
```

---

## Docker Deployment

### Using Docker

#### 1. Build the Image

```bash
docker build -t trading-bot:1.0.0 .
```

#### 2. Run the Container

```bash
docker run -d \
  --name trading-bot \
  -p 5000:5000 \
  -e BINANCE_API_KEY="your_key" \
  -e BINANCE_API_SECRET="your_secret" \
  -v $(pwd)/logs:/app/logs \
  trading-bot:1.0.0
```

#### 3. View Logs

```bash
docker logs -f trading-bot
```

#### 4. Stop the Container

```bash
docker stop trading-bot
docker rm trading-bot
```

### Using Docker Compose

#### 1. Setup

```bash
# Create .env.docker file with your credentials
cp .env.example .env.docker

# Edit .env.docker with your API keys
# BINANCE_API_KEY=your_key
# BINANCE_API_SECRET=your_secret
```

#### 2. Deploy

```bash
# Start services
docker-compose up -d

# View logs
docker-compose logs -f trading-bot

# Stop services
docker-compose down
```

#### 3. Update Image

```bash
docker-compose down
docker build -t trading-bot:latest .
docker-compose up -d
```

---

## Cloud Deployment

### AWS Elastic Beanstalk

#### Prerequisites
- AWS account
- AWS CLI configured
- Elastic Beanstalk CLI installed

#### Steps

```bash
# Initialize Elastic Beanstalk
eb init -p "Python 3.11 running on 64bit Amazon Linux 2" trading-bot --region us-east-1

# Create environment
eb create trading-bot-env

# Deploy application
eb deploy

# View logs
eb logs

# SSH into instance
eb ssh
```

### Heroku

```bash
# Login to Heroku
heroku login

# Create app
heroku create trading-bot-app

# Set environment variables
heroku config:set BINANCE_API_KEY="your_key"
heroku config:set BINANCE_API_SECRET="your_secret"

# Add Procfile (create file named `Procfile`)
echo "web: gunicorn -w 4 -b 0.0.0.0:\$PORT server:app" > Procfile

# Deploy
git push heroku main

# View logs
heroku logs --tail
```

#### Procfile Example

```
web: gunicorn -w 4 -b 0.0.0.0:$PORT server:app
```

### DigitalOcean App Platform

```bash
# Create app.yaml
app_name: trading-bot
env_schema:
  - key: BINANCE_API_KEY
    scope: RUN_TIME
  - key: BINANCE_API_SECRET
    scope: RUN_TIME

services:
- name: trading-bot
  github:
    repo: your-username/binance-futures-trading-bot
    branch: main
  build_command: pip install -r requirements.txt
  run_command: gunicorn -w 4 -b 0.0.0.0:8080 server:app
  http_port: 8080

# Deploy via CLI
doctl apps create --spec app.yaml
```

---

## Production Checklist

### Security

- [ ] API keys are stored in environment variables (never in code)
- [ ] `.env` file is in `.gitignore` and never committed
- [ ] Use separate API keys for testnet and production
- [ ] Enable IP whitelisting on Binance account
- [ ] Set API restrictions to Futures Trading only
- [ ] Disable withdrawal rights on API key
- [ ] Use HTTPS/SSL for web UI (if exposed)
- [ ] Enable firewall rules to restrict access
- [ ] Review security policy in [SECURITY.md](SECURITY.md)

### Deployment

- [ ] All dependencies are pinned in `requirements.txt`
- [ ] Python version is specified (3.9+)
- [ ] Health check is configured
- [ ] Logging is enabled and monitored
- [ ] Backup/recovery plan is documented
- [ ] Secrets are injected at runtime, not build time
- [ ] Container image is scanned for vulnerabilities

### Monitoring

- [ ] Error alerts are configured
- [ ] Log aggregation is set up (ELK, Datadog, etc.)
- [ ] Uptime monitoring is enabled
- [ ] Performance metrics are tracked
- [ ] API rate limits are monitored
- [ ] Order success rate is tracked

### Operations

- [ ] Rollback plan is documented
- [ ] Database backups are scheduled (if applicable)
- [ ] Documentation is up-to-date
- [ ] Team has runbook for common issues
- [ ] Contact information is available
- [ ] Incident response plan is in place

---

## Monitoring & Maintenance

### Log Analysis

```bash
# View recent logs
tail -f logs/trading_bot.log

# Count errors
grep -c "ERROR" logs/trading_bot.log

# Find failed orders
grep "Order failed" logs/trading_bot.log

# Watch for API errors
grep "BinanceAPIError\|API error" logs/trading_bot.log
```

### Health Checks

```bash
# Manual health check
curl http://localhost:5000/api/status

# Automated health check (set up crons)
*/5 * * * * curl -f http://localhost:5000/api/status || alert
```

### Maintenance Tasks

#### Weekly
- [ ] Review logs for errors or warnings
- [ ] Check API rate limit usage
- [ ] Verify balance and positions

#### Monthly
- [ ] Update dependencies: `pip install --upgrade -r requirements.txt`
- [ ] Review and archive old logs
- [ ] Audit orders placed and completion rates

#### Quarterly
- [ ] Rotate API keys
- [ ] Test disaster recovery
- [ ] Review security settings on Binance account
- [ ] Performance optimization review

### Debugging

#### Connection Issues

```bash
# Test API connectivity
python -c "from bot.client import BinanceClient; c = BinanceClient('test', 'test'); print(c.get_server_time())"

# Check network
ping -c 4 testnet.binancefuture.com
```

#### Order Issues

```bash
# Check if symbol exists
python cli.py orders --symbol BTCUSDT

# Dry-run order
python cli.py place --symbol BTCUSDT --side BUY --type MARKET --quantity 0.001 --dry-run

# Check logs
grep "BTCUSDT" logs/trading_bot.log | tail -20
```

#### Performance Issues

```bash
# Monitor resource usage (Docker)
docker stats trading-bot

# Check Python process
ps aux | grep python
```

---

## Disaster Recovery

### Backup Strategy

```bash
# Backup logs daily
*/0 * * * * tar -czf logs/backup/logs_$(date +\%Y\%m\%d).tar.gz logs/trading_bot.log

# Backup configuration
*/0 3 * * * cp .env .env.backup
```

### Recovery Procedures

#### Database Loss
- [ ] Stop the bot
- [ ] Restore `.env` file from backup
- [ ] Restart the bot
- [ ] Verify connectivity: `python cli.py account`

#### System Failure
- [ ] Deploy on new server using Docker/cloud platform
- [ ] Restore configuration from backup
- [ ] Test on testnet first
- [ ] Monitor for 24 hours before production

---

## Performance Optimization

### Gunicorn Configuration

```bash
gunicorn -w 4 \
  --worker-class sync \
  --worker-connections 1000 \
  --max-requests 1000 \
  --timeout 30 \
  --log-level info \
  server:app
```

### Nginx Reverse Proxy

```nginx
upstream trading_bot {
    server localhost:5000;
}

server {
    listen 80;
    server_name tradingbot.example.com;

    location / {
        proxy_pass http://trading_bot;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_buffering off;
    }

    location /api {
        proxy_pass http://trading_bot;
        proxy_set_header Host $host;
        proxy_cache_bypass $http_pragma $http_authorization;
        add_header X-Cache-Status $upstream_cache_status;
    }
}
```

---

## Support

For deployment questions or issues:

1. Check the [README.md](../README.md)
2. Review [SECURITY.md](../SECURITY.md)
3. Open a GitHub issue
4. Contact maintainers

---

**Last Updated**: March 2025
