"""Worker service.

Receives work from the gateway. For Phase 5, POST /process echoes the input.
Later it will call cpp-frame to process image data.
"""

from fastapi import FastAPI
from pydantic import BaseModel, Field

app = FastAPI(title="Worker")


class ProcessRequest(BaseModel):
    """Payload for /process (Phase 5 echo)."""

    numbers: list[int] = Field(
        ...,
        description="List of integers to hand back to the caller.",
    )


@app.get("/health")
def health() -> dict[str, str]:
    """Return the service liveness status.

    Returns:
        Dict with a single 'status' key set to 'ok' when the service is up.
    """
    return {"status": "ok"}


@app.post("/process")
def process(body: ProcessRequest) -> dict[str, list[int]]:
    """Echo the numbers back to prove the gateway-to-worker path works.

    Args:
        body: Client JSON body with a 'numbers' list.

    Returns:
        A dict containing the same 'numbers' list.
    """
    return {"numbers": body.numbers}
