"""Gateway service.

Single entry point for the cloud-microservices system. For now, this service
exposes only a /health endpoint to confirm the service is alive. In later
phases it will also route incoming requests to the worker service.
"""

from fastapi import FastAPI

app = FastAPI(title="Gateway")


@app.get("/health")
def health() -> dict[str, str]:
    """Return the service liveness status.

    Returns:
        Dict with a single 'status' key set to 'ok' when the service is up.
    """
    return {"status": "ok"}
