# Gateway service: cloud-microservices system entry point.

FROM python:3.11-slim

WORKDIR /app

# Install deps before copying app code so the deps layer stays cached
# across most code edits to main.py.
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY main.py .

EXPOSE 8000

# Bind to 0.0.0.0 so the host can reach uvicorn through Docker's bridge.
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
