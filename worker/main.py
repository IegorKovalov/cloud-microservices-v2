"""Worker service.

Receives work from the gateway. For Phase 4 this service only exposes /health.
Later it will call cpp-frame to process image data.
"""

from fastapi import FastAPI

app = FastAPI(title="Worker")


@app.get("/health")
def health() -> dict[str, str]:
    """Return the service liveness status.

    Returns:
        Dict with a single 'status' key set to 'ok' when the service is up.
    """
    return {"status": "ok"}

