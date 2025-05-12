FROM python:3.11-slim

WORKDIR /app

# Copia i file necessari
COPY . .

# Installa le dipendenze
RUN pip install web3 py-solc-x

# Il container sarà in ascolto sulla porta 8545
EXPOSE 8545

# Imposta il comando di avvio
CMD ["python", "automated_deployment.py"]
