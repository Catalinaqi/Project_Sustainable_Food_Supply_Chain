FROM python:3.13.2
WORKDIR /app
COPY on_chain/pyproject.toml on_chain/poetry.lock ./
RUN pip install poetry && poetry install --no-dev
COPY on_chain/ .
CMD ["poetry", "run", "python", "blockchain/web3_handler.py"]