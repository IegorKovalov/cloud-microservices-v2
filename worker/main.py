"""Worker service.

Receives frame payloads from the gateway. Phase 9: POST /process forwards to
cpp-frame POST /process_frame and returns bright_pixel_count.
"""

import os

import requests
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

app = FastAPI(title="Worker")

CPP_FRAME_BASE_URL = os.environ.get(
    "CPP_FRAME_BASE_URL",
    "http://cpp-frame:8002",
)


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
    return {"status": "ok"}


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
    url = f"{CPP_FRAME_BASE_URL.rstrip('/')}/process_frame"
    try:
        response = requests.post(
            url,
            json=body.model_dump(),
            timeout=5.0,
        )
    except requests.RequestException:
        raise HTTPException(
            status_code=502,
            detail="Could not reach the cpp-frame service",
        ) from None

    if not response.ok:
        raise HTTPException(
            status_code=502,
            detail="The cpp-frame service returned an error",
        )

    data = response.json()
    return {"bright_pixel_count": int(data["bright_pixel_count"])}
