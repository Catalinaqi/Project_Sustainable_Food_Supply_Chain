FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy only necessary files
COPY interact_counter.py .
COPY truffle-config.js .
COPY migrations/ ./migrations/
COPY contracts/ ./contracts/

# Set environment variables
ENV GANACHE_HOST=ganache
ENV CONTRACT_PATH=/app/build/contracts/Counter.json

EXPOSE 8545

CMD ["python", "interact_counter.py"]
