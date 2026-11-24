"""Shared menu and order persistence for Pie in the Sky."""

import csv
import json
import re
import threading
import uuid
from datetime import datetime, timezone
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path


PROJECT_DIR = Path(__file__).resolve().parent
MENU_FILES = (PROJECT_DIR / "menu.txt", PROJECT_DIR / "dessert_menu.txt")
ORDERS_FILE = PROJECT_DIR / "orders.csv"

_ORDERS_LOCK = threading.Lock()


def menu_item_details(item):
    """Return a display name and price, or None when no price is listed."""
    match = re.fullmatch(r"(.+?)\s+\(\$(\d+(?:\.\d{1,2})?)\)", item)
    if not match:
        return item, None
    return match.group(1), Decimal(match.group(2))


def calculate_order_total(items):
    """Calculate subtotal, Woodstock sales tax, total, and unpriced items."""
    subtotal = Decimal("0.00")
    unpriced = []
    for selected in items:
        _, price = menu_item_details(selected["item"])
        if price is None:
            unpriced.append(selected["item"])
        else:
            subtotal += price

    tax = (subtotal * Decimal("0.0875")).quantize(
        Decimal("0.01"), rounding=ROUND_HALF_UP
    )
    return subtotal, tax, subtotal + tax, unpriced


def load_menu(menu_files=MENU_FILES):
    """Load category/item pairs from the restaurant's text menu files."""
    menu = {}
    for menu_file in menu_files:
        with open(menu_file, encoding="utf-8") as file:
            for line_number, line in enumerate(file, start=1):
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                if ":" not in line:
                    raise ValueError(
                        f"Invalid menu format in {menu_file} on line {line_number}."
                    )

                category, item_list = line.split(":", 1)
                category = category.strip()
                items = [item.strip() for item in item_list.split(",") if item.strip()]
                if not category or not items:
                    raise ValueError(
                        f"Invalid menu format in {menu_file} on line {line_number}."
                    )

                category_items = menu.setdefault(category, [])
                for item in items:
                    existing_items = {existing.casefold() for existing in category_items}
                    if item.casefold() not in existing_items:
                        category_items.append(item)

    return menu


def create_order(customer_name, selected_items, menu, orders_file=ORDERS_FILE):
    """Validate and persist an order made up of category/item dictionaries."""
    if not isinstance(customer_name, str):
        raise ValueError("Please enter a customer name.")
    customer_name = customer_name.strip()
    if not customer_name:
        raise ValueError("Please enter a customer name.")
    if not isinstance(selected_items, list) or not selected_items:
        raise ValueError("Please select at least one menu item.")

    items = []
    for selection in selected_items:
        if not isinstance(selection, dict):
            raise ValueError("Each selected item must include a category and item.")
        category = selection.get("category")
        name = selection.get("item")
        if not isinstance(category, str) or not isinstance(name, str):
            raise ValueError("Each selected item must include a category and item.")

        valid_items = menu.get(category, [])
        matched_item = next(
            (item for item in valid_items if item.casefold() == name.strip().casefold()),
            None,
        )
        if matched_item is None:
            raise ValueError(f"{name!r} is not available in the {category!r} menu.")
        if menu_item_details(matched_item)[1] is None:
            raise ValueError(f"{matched_item!r} does not have a price yet.")

        normalized_addons = selection.get("addons", [])
        if not isinstance(normalized_addons, list) or any(
            addon not in ("milk", "sugar") for addon in normalized_addons
        ):
            raise ValueError("Drink add-ons may only be milk or sugar.")
        if normalized_addons:
            base_name = re.sub(
                r"\s+\(\$\d+(?:\.\d{1,2})?\)$", "", matched_item
            ).casefold()
            if category.casefold() != "drinks" or base_name not in (
                "tea",
                "coffee",
                "decaf",
            ):
                raise ValueError("Milk and sugar are only available for tea or coffee.")

        order_item = {"category": category, "item": matched_item}
        if normalized_addons:
            order_item["addons"] = list(dict.fromkeys(normalized_addons))
        items.append(order_item)

    order = {
        "order_id": str(uuid.uuid4()),
        "timestamp": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "customer_name": customer_name,
        "items": items,
    }

    orders_file = Path(orders_file)
    with _ORDERS_LOCK:
        needs_header = not orders_file.exists() or orders_file.stat().st_size == 0
        with orders_file.open("a", newline="", encoding="utf-8") as file:
            writer = csv.DictWriter(
                file,
                fieldnames=("order_id", "timestamp", "customer_name", "items"),
            )
            if needs_header:
                writer.writeheader()
            writer.writerow(
                {
                    **order,
                    "items": json.dumps(order["items"], ensure_ascii=False),
                }
            )
    return order


def read_orders(orders_file=ORDERS_FILE, limit=20):
    """Return the most recent saved orders, newest first."""
    orders_file = Path(orders_file)
    if not orders_file.exists():
        return []

    with orders_file.open(newline="", encoding="utf-8") as file:
        orders = []
        for row in csv.DictReader(file):
            orders.append(
                {
                    "order_id": row["order_id"],
                    "timestamp": row["timestamp"],
                    "customer_name": row["customer_name"],
                    "items": json.loads(row["items"]),
                }
            )
    return list(reversed(orders[-limit:]))
