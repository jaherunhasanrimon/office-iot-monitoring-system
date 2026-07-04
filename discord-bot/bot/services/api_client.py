"""
API client — makes non-blocking HTTP requests to the Flask backend using asyncio.to_thread.
"""

import os
import requests
import asyncio

BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:5000")


async def get(path: str) -> dict | list | None:
    """GET a backend endpoint asynchronously. Returns parsed JSON or None on failure."""
    def _fetch():
        resp = requests.get(f"{BACKEND_URL}{path}", timeout=5)
        resp.raise_for_status()
        return resp.json()

    try:
        return await asyncio.to_thread(_fetch)
    except Exception as e:
        print(f"[API Client] Error fetching {path}: {e}")
        return None
