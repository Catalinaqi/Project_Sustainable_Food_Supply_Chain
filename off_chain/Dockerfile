FROM python:3.13.2
WORKDIR /app
COPY off_chain/pyproject.toml off_chain/poetry.lock ./
RUN pip install poetry && poetry install --no-dev
COPY off_chain/ .
CMD ["poetry", "run", "python", "app.py"]