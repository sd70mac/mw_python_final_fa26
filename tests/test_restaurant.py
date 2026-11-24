import csv
import tempfile
import unittest
from datetime import datetime
from decimal import Decimal
from pathlib import Path

from restaurant import (
    CENTRAL_TIME,
    calculate_order_total,
    create_order,
    format_central_timestamp,
    load_menu,
    read_orders,
    prepare_order,
)


class RestaurantTests(unittest.TestCase):
    def test_load_menu_merges_categories_and_ignores_duplicate_items(self):
        with tempfile.TemporaryDirectory() as directory:
            first = Path(directory) / "menu.txt"
            second = Path(directory) / "dessert_menu.txt"
            first.write_text(
                "# menu note\nPIES : Apple, Custard\nDRINKS : Tea\n",
                encoding="utf-8",
            )
            second.write_text("PIES : Custard, Blueberry\n", encoding="utf-8")

            self.assertEqual(
                load_menu((first, second)),
                {"PIES": ["Apple", "Custard", "Blueberry"], "DRINKS": ["Tea"]},
            )

    def test_create_order_persists_items_and_rejects_unavailable_items(self):
        with tempfile.TemporaryDirectory() as directory:
            orders_file = Path(directory) / "orders.csv"
            menu = {"PIES": ["Apple ($12)"]}

            order = create_order(
                "Casey",
                [{"category": "PIES", "item": "apple ($12)"}],
                menu,
                orders_file,
            )

            self.assertEqual(order["customer_name"], "Casey")
            self.assertEqual(
                order["items"],
                [{"category": "PIES", "item": "Apple ($12)"}],
            )
            self.assertEqual(read_orders(orders_file), [order])
            with orders_file.open(newline="", encoding="utf-8") as file:
                self.assertEqual(len(list(csv.DictReader(file))), 1)

            with self.assertRaisesRegex(ValueError, "not available"):
                create_order(
                    "Casey",
                    [{"category": "PIES", "item": "Pumpkin"}],
                    menu,
                    orders_file,
                )

    def test_create_order_requires_customer_and_items(self):
        with self.assertRaisesRegex(ValueError, "customer name"):
            create_order(" ", [{"category": "PIES", "item": "Apple"}], {"PIES": ["Apple"]})
        with self.assertRaisesRegex(ValueError, "at least one"):
            create_order("Casey", [], {"PIES": ["Apple ($12)"]})

    def test_create_order_rejects_unpriced_items(self):
        with self.assertRaisesRegex(ValueError, "does not have a price"):
            create_order(
                "Casey",
                [{"category": "PIES", "item": "Shepherds'"}],
                {"PIES": ["Shepherds'"]},
                Path("unused-test-orders.csv"),
            )

    def test_calculate_order_total_counts_repeats_and_reports_unpriced_items(self):
        subtotal, tax, total, unpriced = calculate_order_total(
            [
                {"item": "Apple ($12)"},
                {"item": "Apple ($12)"},
                {"item": "Tea ($2)"},
                {"item": "Shepherds'"},
            ]
        )

        self.assertEqual(
            (subtotal, tax, total),
            (Decimal("26.00"), Decimal("2.28"), Decimal("28.28")),
        )
        self.assertEqual(unpriced, ["Shepherds'"])

    def test_create_order_persists_supported_drink_addons(self):
        with tempfile.TemporaryDirectory() as directory:
            order = create_order(
                "Casey",
                [
                    {
                        "category": "DRINKS",
                        "item": "Tea ($2)",
                        "addons": ["milk", "sugar"],
                    }
                ],
                {"DRINKS": ["Tea ($2)"]},
                Path(directory) / "orders.csv",
            )

        self.assertEqual(
            order["items"],
            [
                {
                    "category": "DRINKS",
                    "item": "Tea ($2)",
                    "addons": ["milk", "sugar"],
                }
            ],
        )

    def test_order_timestamps_are_created_in_central_time(self):
        order = prepare_order(
            "Casey",
            [{"category": "PIES", "item": "Apple ($12)"}],
            {"PIES": ["Apple ($12)"]},
        )

        timestamp = datetime.fromisoformat(order["timestamp"])
        self.assertEqual(timestamp.utcoffset(), datetime.now(CENTRAL_TIME).utcoffset())

    def test_format_central_timestamp_handles_standard_and_daylight_time(self):
        self.assertEqual(
            format_central_timestamp("2026-01-15T12:00:00+00:00"),
            "2026-01-15 06:00:00 AM CST",
        )
        self.assertEqual(
            format_central_timestamp("2026-07-15T12:00:00Z"),
            "2026-07-15 07:00:00 AM CDT",
        )

    def test_create_order_rejects_addons_for_non_coffee_drinks(self):
        with self.assertRaisesRegex(ValueError, "only available for tea or coffee"):
            create_order(
                "Casey",
                [
                    {
                        "category": "DRINKS",
                        "item": "Lemonade ($2)",
                        "addons": ["milk"],
                    }
                ],
                {"DRINKS": ["Lemonade ($2)"]},
                Path("unused-test-orders.csv"),
            )


if __name__ == "__main__":
    unittest.main()
