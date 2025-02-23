#!/bin/bash

# Функция для проверки доступности PostgreSQL
wait_for_postgres() {
    echo "Waiting for PostgreSQL..."
    while ! nc -z postgres ${POSTGRES_PORT}; do
        sleep 0.1
    done
    echo "PostgreSQL is ready"
}

# Ждем готовности сервисов
wait_for_postgres

# Применяем миграции
echo "Applying database migrations..."
alembic upgrade head

# Запускаем приложение
echo "Starting FastAPI application..."
uvicorn src.main:create_application --host ${SERVER_HOST} --port ${SERVER_PORT} --factory