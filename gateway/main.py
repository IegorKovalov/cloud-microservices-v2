"""Gateway service.

Single entry point for the cloud-microservices system. Exposes /health and /process;
/process forwards JSON to the worker over HTTP (Phase 9: worker calls cpp-frame).
"""

import os

import requests
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

app = FastAPI(title="Gateway")

WORKER_BASE_URL = os.environ.get("WORKER_BASE_URL", "http://worker:8001")


class ProcessRequest(BaseModel):
    """Payload for /process (forwarded to the worker)."""

    pixels: list[float] = Field(
        ...,
        description="Pixel intensity values passed through to cpp-frame.",
    )
    threshold: float = Field(
        ...,
        description="Brightness cutoff forwarded to cpp-frame.",
    )


@app.get("/health")
def health() -> dict[str, str]:
    """Return the service liveness status.

    Returns:
        Dict with a single 'status' key set to 'ok' when the service is up.
    """
    return {"status": "ok"}


@app.post("/process")
def process(body: ProcessRequest) -> dict:
    """Forward frame payload to the worker and return cpp-frame's count.

    Args:
        body: JSON body with 'pixels' and 'threshold'.

    Returns:
        JSON object from the worker (bright_pixel_count) on success.

    Raises:
        HTTPException: 502 if the worker cannot be reached or returns an error.
    """
    url = f"{WORKER_BASE_URL.rstrip('/')}/process"
    try:
        response = requests.post(
            url,
            json=body.model_dump(),
            timeout=5.0,
        )
    except requests.RequestException:
        raise HTTPException(
            status_code=502,
            detail="Could not reach the worker service",
        ) from None

    if not response.ok:
        raise HTTPException(
            status_code=502,
            detail="The worker service returned an error",
        )

    return response.json()
