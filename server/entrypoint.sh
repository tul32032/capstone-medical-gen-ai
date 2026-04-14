#!/bin/sh

echo "Running migrations..."
uv run python manage.py makemigrations
uv run python manage.py migrate

echo "Starting server..."
uv run gunicorn betesbot.wsgi:application --bind 0.0.0.0:8000 --workers 4 --timeout 180
