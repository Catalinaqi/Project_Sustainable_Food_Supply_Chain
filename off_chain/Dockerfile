FROM python:3.13.2
WORKDIR /app
COPY pyproject.toml poetry.lock ./
RUN pip install poetry && poetry install --no-dev
COPY  .
CMD ["poetry", "run", "python", "app.py"]