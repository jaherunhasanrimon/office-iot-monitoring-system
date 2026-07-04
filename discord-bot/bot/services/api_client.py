"""
API client — makes HTTP requests to the Flask backend.
"""

import os
import requests

BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:5000")


def get(path: str) -> dict | list | None:
    """GET a backend endpoint. Returns parsed JSON or None on failure."""
    try:
        resp = requests.get(f"{BACKEND_URL}{path}", timeout=5)
        resp.raise_for_status()
        return resp.json()
    except Exception as e:
        print(f"[API Client] Error fetching {path}: {e}")
        return None
