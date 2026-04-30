"""Pure-Python checks that mirror cpp-frame counting rules (no binary)."""

from __future__ import annotations


def bright_pixel_count(pixels: list[float], threshold: float) -> int:
    """Same rule as cpp-frame: count pixels where value >= threshold."""
    return sum(1 for p in pixels if p >= threshold)


def test_bright_pixel_count_includes_threshold_boundary():
    """Values equal to the threshold count as bright (>=)."""
    assert bright_pixel_count([0.1, 0.9, 0.5], 0.5) == 2


def test_bright_pixel_count_empty_frame():
    """An empty pixel list yields zero bright pixels."""
    assert bright_pixel_count([], 0.5) == 0
