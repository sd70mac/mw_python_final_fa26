"""HTTP client used by the console and Streamlit applications."""

import json
import os
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


API_URL = os.environ.get("PIE_API_URL", "http://127.0.0.1:8000").rstrip("/")


def _request(path, method="GET", payload=None):
    data = None if payload is None else json.dumps(payload).encode("utf-8")
    request = Request(
        f"{API_URL}{path}",
        data=data,
        headers={"Content-Type": "application/json"},
        method=method,
    )
    try:
        with urlopen(request, timeout=5) as response:
            return json.loads(response.read().decode("utf-8"))
    except HTTPError as error:
        with error:
            detail = error.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"Order service returned HTTP {error.code}: {detail}") from error
    except URLError as error:
        raise RuntimeError(
            "Cannot reach the order service. Start it with `python api_server.py`."
        ) from error


def get_menu():
    return _request("/menu")


def get_orders():
    return _request("/orders")


def submit_order(customer_name, selected_items):
    return _request(
        "/orders",
        method="POST",
        payload={"customer_name": customer_name, "items": selected_items},
    )
