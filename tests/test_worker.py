"""Worker HTTP tests (mocked cpp-frame via ``requests``)."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest
import requests
from fastapi.testclient import TestClient

from tests.helpers import load_worker_main


@pytest.fixture
def worker_client():
    """Fresh TestClient bound to the worker app."""
    mod = load_worker_main()
    return TestClient(mod.app), mod


def test_process_returns_cpp_frame_count(worker_client):
    """cpp-frame JSON is normalized to an integer bright_pixel_count."""
    client, mod = worker_client
    mock_resp = MagicMock()
    mock_resp.ok = True
    mock_resp.json.return_value = {"bright_pixel_count": 3}

    with patch.object(mod, "requests") as req:
        req.post.return_value = mock_resp
        response = client.post(
            "/process",
            json={"pixels": [1.0, 1.0, 1.0], "threshold": 0.5},
        )

    assert response.status_code == 200
    assert response.json() == {"bright_pixel_count": 3}


def test_process_502_when_cpp_frame_unreachable(worker_client):
    """Connection errors to cpp-frame become HTTP 502."""
    client, mod = worker_client

    with patch.object(mod, "requests") as req:
        req.post.side_effect = requests.RequestException("no route")
        response = client.post(
            "/process",
            json={"pixels": [0.5], "threshold": 0.5},
        )

    assert response.status_code == 502
