"""Helpers to load gateway/worker apps without ``main`` module clashes."""

from __future__ import annotations

import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def load_gateway_main():
    """Load ``gateway/main.py`` as a uniquely named module."""
    spec = importlib.util.spec_from_file_location(
        "gateway_main",
        ROOT / "gateway" / "main.py",
    )
    assert spec is not None and spec.loader is not None
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def load_worker_main():
    """Load ``worker/main.py`` as a uniquely named module."""
    spec = importlib.util.spec_from_file_location(
        "worker_main",
        ROOT / "worker" / "main.py",
    )
    assert spec is not None and spec.loader is not None
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod
