# Worker service: receives work from the gateway (cpp-frame integration later).

FROM python:3.11-slim

WORKDIR /app

# Install deps before copying app code so the deps layer stays cached
# across most code edits to main.py.
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY main.py .

EXPOSE 8001

# Bind to 0.0.0.0 so other containers (e.g. gateway) can reach this service.
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8001"]
