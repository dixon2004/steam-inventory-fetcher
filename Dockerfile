FROM python:3.10.10-slim

WORKDIR /apps/steam-inventory-fetcher

COPY . .

RUN apt-get update && apt-get install -y --no-install-recommends curl && \
    pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

WORKDIR /apps/steam-inventory-fetcher/src

EXPOSE 8080

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]