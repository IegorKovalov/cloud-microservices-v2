"""Gateway service.

Single entry point for the cloud-microservices system. Exposes /health, /metrics,
and /process; /process forwards JSON to the worker over HTTP.
"""

import os
import threading

import requests
from requests import RequestException
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

app = FastAPI(title="Gateway")

WORKER_BASE_URL = os.environ.get("WORKER_BASE_URL", "http://worker:8001")

_metrics_lock = threading.Lock()
_request_count = 0
_error_count = 0


def _inc_request() -> None:
    """Increment total observed HTTP requests (handler entry)."""
    global _request_count
    with _metrics_lock:
        _request_count += 1


def _inc_error() -> None:
    """Increment error counter (failed downstream /process)."""
    global _error_count
    with _metrics_lock:
        _error_count += 1


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
    _inc_request()
    return {"status": "ok"}


@app.get("/metrics")
def metrics() -> dict[str, int]:
    """Return simple request and error counters.

    Returns:
        Dict with request_count and error_count (monotonic since process start).
    """
    _inc_request()
    with _metrics_lock:
        return {
            "request_count": _request_count,
            "error_count": _error_count,
        }


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
    _inc_request()
    url = f"{WORKER_BASE_URL.rstrip('/')}/process"
    try:
        response = requests.post(
            url,
            json=body.model_dump(),
            timeout=5.0,
        )
    except RequestException:
        _inc_error()
        raise HTTPException(
            status_code=502,
            detail="Could not reach the worker service",
        ) from None

    if not response.ok:
        _inc_error()
        raise HTTPException(
            status_code=502,
            detail="The worker service returned an error",
        )

    return response.json()
