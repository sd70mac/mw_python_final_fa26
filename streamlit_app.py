"""Streamlit ordering page for Pie in the Sky."""

from collections import Counter

import streamlit as st
from streamlit.errors import StreamlitSecretNotFoundError

from api_client import configure_supabase, get_menu, get_orders, submit_order
from restaurant import calculate_order_total, menu_item_details


# CHANGE LOG - CLI ordering features moved into the existing API-backed page:
# - Uses Supabase for hosted orders and the local API for development.
# - Replaced the one-item-per-category form with quantity and drink add-on widgets.
# - Added itemized prices, tax calculation, and an order summary.
# - Added menu entries from the CLI project while preserving this repository's items.
# - Keeps customer order history private to the restaurant console.

BEVERAGES_WITH_ADDONS = {"tea", "coffee", "decaf"}
CART_WIDGET_PREFIXES = ("selected_", "quantity_", "milk_", "sugar_")


def clear_order_cart():
    """Clear the session cart and its Streamlit widget values."""
    for key in list(st.session_state):
        if key.startswith(CART_WIDGET_PREFIXES):
            del st.session_state[key]
    st.session_state["order_cart"] = []


def format_menu_item(item):
    """Format a menu item for display without changing its API value."""
    name, price = menu_item_details(item)
    if price is None:
        return f"{name} — price not set"
    return f"{name} — ${price:.2f}"


def order_item_label(item):
    """Format a persisted order item, including optional drink add-ons."""
    name, _ = menu_item_details(item["item"])
    addons = item.get("addons", [])
    if addons:
        name = f"{name} with {' and '.join(addons)}"
    return name


def selected_menu_items(menu):
    """Show category widgets and return item records, including quantities/add-ons."""
    selected_items = []
    for category, items in menu.items():
        selections = st.multiselect(
            category.title(),
            items,
            format_func=format_menu_item,
            key=f"selected_{category}",
        )
        for item in selections:
            name, _ = menu_item_details(item)
            quantity = st.number_input(
                f"{name} quantity",
                min_value=1,
                max_value=20,
                value=1,
                step=1,
                key=f"quantity_{category}_{item}",
            )
            addons = []
            if category.casefold() == "drinks" and name.casefold() in BEVERAGES_WITH_ADDONS:
                addon_columns = st.columns(2)
                if addon_columns[0].checkbox(
                    f"Add milk to {name}",
                    key=f"milk_{category}_{item}",
                ):
                    addons.append("milk")
                if addon_columns[1].checkbox(
                    f"Add sugar to {name}",
                    key=f"sugar_{category}_{item}",
                ):
                    addons.append("sugar")

            for _ in range(quantity):
                selected = {"category": category, "item": item}
                if addons:
                    selected["addons"] = addons
                selected_items.append(selected)
    return selected_items


def popular_order_summaries(orders):
    """Return the ten most frequent anonymized item combinations."""
    counts = Counter(
        tuple(sorted(order_item_label(item) for item in order["items"]))
        for order in orders
        if order.get("items")
    )
    return counts.most_common(10)


st.set_page_config(page_title="Pie in the Sky", page_icon="PI", layout="wide")
st.title("Pie in the Sky Ordering Kiosk")
st.caption("A neighborhood restaurant in Woodstock, Illinois")

if "order_cart" not in st.session_state:
    st.session_state["order_cart"] = []
if st.session_state.pop("reset_order_widgets", False):
    clear_order_cart()
if "last_order_id" in st.session_state:
    st.success(f"Order received. Your order number is {st.session_state['last_order_id']}.")

try:
    supabase_url = st.secrets["SUPABASE_URL"]
    supabase_secret_key = st.secrets["SUPABASE_SECRET_KEY"]
except StreamlitSecretNotFoundError:
    pass
except KeyError:
    st.error("Configure SUPABASE_URL and SUPABASE_SECRET_KEY in Streamlit secrets.")
    st.stop()
else:
    try:
        configure_supabase(supabase_url, supabase_secret_key)
    except ValueError as error:
        st.error(f"Invalid Supabase configuration: {error}")
        st.stop()

try:
    menu = get_menu()
except RuntimeError as error:
    st.error(str(error))
    st.stop()

try:
    recent_orders = get_orders()
except RuntimeError as error:
    st.error(str(error))
    recent_orders = []

customer_name = st.text_input("Your name", value="").strip()

with st.expander("View Menu", expanded=False):
    for category, items in menu.items():
        st.write(f"**{category.title()}**")
        for item in items:
            st.write(f"- {format_menu_item(item)}")

st.subheader("Choose Items")
st.button("Clear order", on_click=clear_order_cart)
st.session_state["order_cart"] = selected_menu_items(menu)
selected_items = st.session_state["order_cart"]

st.subheader("Full Order")
if selected_items:
    order_lines = Counter(
        (order_item_label(item), menu_item_details(item["item"])[1])
        for item in selected_items
    )
    for (name, unit_price), quantity in order_lines.items():
        if unit_price is None:
            price_text = "price not set"
        elif quantity > 1:
            price_text = (
                f"${unit_price:.2f} each × {quantity} "
                f"= ${unit_price * quantity:.2f}"
            )
        else:
            price_text = f"${unit_price:.2f}"
        st.write(f"- {name} — {price_text}")
else:
    st.info("No items selected yet.")

subtotal, tax, grand_total, unpriced_items = calculate_order_total(selected_items)
st.write(f"**Subtotal:** ${subtotal:.2f}")
st.write("**Woodstock, Illinois Sales Tax:** 8.75%")
st.write(f"**Total:** ${grand_total:.2f}")
if unpriced_items:
    st.warning(
        "Some selected items do not have a price yet: "
        + ", ".join(sorted(set(unpriced_items)))
        + ". Add prices to the menu before placing this order."
    )

if st.button(
    "Place Order",
    type="primary",
    disabled=not selected_items or bool(unpriced_items) or not customer_name,
):
    try:
        order = submit_order(customer_name, selected_items)
    except (RuntimeError, ValueError) as error:
        st.error(f"Could not place order: {error}")
    else:
        st.session_state["last_order_id"] = order["order_id"][:8]
        st.session_state["reset_order_widgets"] = True
        st.rerun()

st.subheader("Popular Orders")
st.caption(
    "Customer order details are private to the restaurant; only anonymized item "
    "combinations are shown here."
)
popular_orders = popular_order_summaries(recent_orders)
if not popular_orders:
    st.caption("No popular orders yet.")
for items, count in popular_orders:
    st.write(f"- {', '.join(items)} ({count} orders)")
