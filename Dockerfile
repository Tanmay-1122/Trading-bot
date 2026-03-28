FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Environment variables (set at runtime via -e or docker-compose)
ENV BINANCE_API_KEY=""
ENV BINANCE_API_SECRET=""
ENV PORT=5000
ENV LOG_LEVEL=INFO

# Expose port
EXPOSE 5000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:5000/api/status')" || exit 1

# Run Flask server
CMD ["python", "server.py"]
