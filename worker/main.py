"""Worker service.

Receives frame payloads from the gateway. POST /process forwards to
cpp-frame POST /process_frame and returns bright_pixel_count.
"""

import os
import threading

import requests
from requests import RequestException
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

app = FastAPI(title="Worker")

CPP_FRAME_BASE_URL = os.environ.get(
    "CPP_FRAME_BASE_URL",
    "http://cpp-frame:8002",
)

_metrics_lock = threading.Lock()
_request_count = 0
_error_count = 0


def _inc_request() -> None:
    """Increment total observed HTTP requests (handler entry)."""
    global _request_count
    with _metrics_lock:
        _request_count += 1


def _inc_error() -> None:
    """Increment error counter (failed cpp-frame call)."""
    global _error_count
    with _metrics_lock:
        _error_count += 1


class ProcessRequest(BaseModel):
    """Payload for /process (forwarded to cpp-frame)."""

    pixels: list[float] = Field(
        ...,
        description="Pixel intensity values for cpp-frame.",
    )
    threshold: float = Field(
        ...,
        description="Brightness cutoff; pixels >= threshold count as bright.",
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
def process(body: ProcessRequest) -> dict[str, int]:
    """Forward pixels and threshold to cpp-frame and return its count.

    Args:
        body: JSON with 'pixels' and 'threshold'.

    Returns:
        Dict with 'bright_pixel_count' from cpp-frame.

    Raises:
        HTTPException: 502 if cpp-frame cannot be reached or returns an error.
    """
    _inc_request()
    url = f"{CPP_FRAME_BASE_URL.rstrip('/')}/process_frame"
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
            detail="Could not reach the cpp-frame service",
        ) from None

    if not response.ok:
        _inc_error()
        raise HTTPException(
            status_code=502,
            detail="The cpp-frame service returned an error",
        )

    data = response.json()
    return {"bright_pixel_count": int(data["bright_pixel_count"])}
