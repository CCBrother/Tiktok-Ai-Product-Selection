FROM python:3.11-slim

WORKDIR /app
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

COPY pyproject.toml README.md ./
COPY backend ./backend
COPY ai_product_radar ./ai_product_radar

RUN pip install --no-cache-dir -e .

EXPOSE 8000
