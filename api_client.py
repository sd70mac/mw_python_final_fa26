"""Order storage clients for local development and the hosted Supabase database."""

import json
import os
from urllib.error import HTTPError, URLError
from urllib.parse import urlparse
from urllib.request import Request, urlopen

from restaurant import load_menu, prepare_order


API_URL = os.environ.get("PIE_API_URL", "http://127.0.0.1:8000").rstrip("/")
_SUPABASE_URL = os.environ.get("PIE_SUPABASE_URL", "").strip().rstrip("/")
_SUPABASE_KEY = os.environ.get("PIE_SUPABASE_KEY", "").strip()
_ORDERS_QUERY = (
    "orders?select=order_id,timestamp,customer_name,items"
    "&order=timestamp.desc&limit=20"
)


def configure_supabase(url, service_role_key):
    """Configure the hosted database using server-side credentials."""
    global _SUPABASE_URL, _SUPABASE_KEY

    if not isinstance(url, str) or not isinstance(service_role_key, str):
        raise ValueError("Supabase URL and service role key must be strings.")
    url = url.strip().rstrip("/")
    service_role_key = service_role_key.strip()
    parsed_url = urlparse(url)
    if parsed_url.scheme != "https" or not parsed_url.netloc:
        raise ValueError("Supabase URL must be an HTTPS URL.")
    if not service_role_key:
        raise ValueError("Supabase service role key cannot be empty.")

    _SUPABASE_URL = url
    _SUPABASE_KEY = service_role_key


def _supabase_is_configured():
    if bool(_SUPABASE_URL) != bool(_SUPABASE_KEY):
        raise RuntimeError(
            "Set both PIE_SUPABASE_URL and PIE_SUPABASE_KEY to use Supabase."
        )
    return bool(_SUPABASE_URL)


def _local_request(path, method="GET", payload=None):
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
        raise RuntimeError(
            f"Order service returned HTTP {error.code}: {detail}"
        ) from error
    except URLError as error:
        raise RuntimeError(
            "Cannot reach the order backend. For local use, start "
            "`python api_server.py`; for Streamlit Cloud, configure Supabase secrets."
        ) from error


def _supabase_request(path, method="GET", payload=None):
    if not _supabase_is_configured():
        raise RuntimeError("Supabase has not been configured.")

    headers = {
        "apikey": _SUPABASE_KEY,
        "Authorization": f"Bearer {_SUPABASE_KEY}",
        "Content-Type": "application/json",
    }
    if method == "POST":
        headers["Prefer"] = "return=representation"

    data = None if payload is None else json.dumps(payload).encode("utf-8")
    request = Request(
        f"{_SUPABASE_URL}/rest/v1/{path}",
        data=data,
        headers=headers,
        method=method,
    )
    try:
        with urlopen(request, timeout=10) as response:
            return json.loads(response.read().decode("utf-8"))
    except HTTPError as error:
        with error:
            detail = error.read().decode("utf-8", errors="replace")
        raise RuntimeError(
            f"Supabase returned HTTP {error.code}: {detail}"
        ) from error
    except URLError as error:
        raise RuntimeError(
            "Cannot reach Supabase. Check the project URL and network connection."
        ) from error
    except json.JSONDecodeError as error:
        raise RuntimeError("Supabase returned an invalid JSON response.") from error


def get_menu():
    if _supabase_is_configured():
        try:
            return load_menu()
        except (OSError, ValueError) as error:
            raise RuntimeError(f"Could not load the menu files: {error}") from error
    return _local_request("/menu")


def get_orders():
    if _supabase_is_configured():
        orders = _supabase_request(_ORDERS_QUERY)
        if not isinstance(orders, list):
            raise RuntimeError("Supabase returned an invalid orders response.")
        return orders
    return _local_request("/orders")


def submit_order(customer_name, selected_items):
    if _supabase_is_configured():
        try:
            order = prepare_order(customer_name, selected_items, load_menu())
        except OSError as error:
            raise RuntimeError(f"Could not load the menu files: {error}") from error
        rows = _supabase_request("orders", method="POST", payload=order)
        if not isinstance(rows, list) or not rows:
            raise RuntimeError("Supabase did not return the saved order.")
        return rows[0]
    return _local_request(
        "/orders",
        method="POST",
        payload={"customer_name": customer_name, "items": selected_items},
    )
