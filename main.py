"""Console ordering client for Pie in the Sky."""

import sys

from api_client import get_menu, get_orders, submit_order
from restaurant import calculate_order_total, format_central_timestamp


def show_recent_orders(orders):
    """Print orders saved through either the web page or console."""
    print("\nRecent orders:")
    if not orders:
        print("  No orders have been placed yet.")
        return

    for order in orders:
        items = ", ".join(
            item["item"]
            + (
                f" with {' and '.join(item['addons'])}"
                if item.get("addons")
                else ""
            )
            for item in order["items"]
        )
        order_time = format_central_timestamp(order["timestamp"])
        print(f"  {order['customer_name']}: {items} ({order_time})")


def choose_items(menu):
    """Prompt for one or more numbered menu items."""
    options = []
    print("\nMenu:")
    for category, items in menu.items():
        print(f"\n{category}:")
        for item in items:
            options.append({"category": category, "item": item})
            print(f"  {len(options)}. {item}")

    while True:
        answer = input(
            "\nEnter item numbers separated by commas "
            "(repeat a number for extra quantity): "
        )
        try:
            numbers = [int(value.strip()) for value in answer.split(",")]
            if not numbers or any(
                number < 1 or number > len(options) for number in numbers
            ):
                raise ValueError
        except ValueError:
            print(f"Choose numbers from 1 to {len(options)}.")
            continue
        selected_items = [options[number - 1] for number in numbers]
        _, _, _, unpriced_items = calculate_order_total(selected_items)
        if unpriced_items:
            print(
                "These items do not have prices yet and cannot be ordered: "
                + ", ".join(sorted(set(unpriced_items)))
            )
            continue
        return selected_items


def main():
    try:
        menu = get_menu()
        show_recent_orders(get_orders())
        customer_name = input("\nCustomer name: ")
        selected_items = choose_items(menu)
        order = submit_order(customer_name, selected_items)
    except (RuntimeError, ValueError) as error:
        print(f"Could not place order: {error}", file=sys.stderr)
        return 1
    except (EOFError, KeyboardInterrupt):
        print("\nOrder cancelled.")
        return 1

    print(f"\nOrder received: {order['order_id'][:8]}")
    subtotal, tax, total, _ = calculate_order_total(order["items"])
    print(f"Subtotal: ${subtotal:.2f}")
    print(f"Woodstock sales tax (8.75%): ${tax:.2f}")
    print(f"Total: ${total:.2f}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
