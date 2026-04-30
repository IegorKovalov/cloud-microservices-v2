"""Gateway HTTP tests (mocked worker via ``requests``)."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest
import requests
from fastapi.testclient import TestClient

from tests.helpers import load_gateway_main


@pytest.fixture
def gateway_client():
    """Fresh TestClient bound to the gateway app."""
    mod = load_gateway_main()
    return TestClient(mod.app), mod


def test_process_returns_worker_payload(gateway_client):
    """Successful worker response is passed through to the client."""
    client, mod = gateway_client
    mock_resp = MagicMock()
    mock_resp.ok = True
    mock_resp.json.return_value = {"bright_pixel_count": 2}

    with patch.object(mod, "requests") as req:
        req.post.return_value = mock_resp
        response = client.post(
            "/process",
            json={"pixels": [0.1, 0.9, 0.5], "threshold": 0.5},
        )

    assert response.status_code == 200
    assert response.json() == {"bright_pixel_count": 2}
    req.post.assert_called_once()


def test_process_502_when_worker_unreachable(gateway_client):
    """Network failure talking to the worker becomes HTTP 502."""
    client, mod = gateway_client

    with patch.object(mod, "requests") as req:
        req.post.side_effect = requests.RequestException("boom")
        response = client.post(
            "/process",
            json={"pixels": [1.0], "threshold": 0.0},
        )

    assert response.status_code == 502
