FROM python:3.13-slim
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /app

RUN apt-get update \
    && apt-get install -y netcat-traditional

COPY pyproject.toml poetry.lock ./
RUN pip install --no-cache-dir poetry \
    && poetry config virtualenvs.create false \
    && poetry install --without dev --no-interaction --no-ansi

COPY . .

RUN chmod +x scripts/start.sh

CMD ["./scripts/start.sh"]