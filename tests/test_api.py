import tempfile
import threading
import unittest
from http.server import ThreadingHTTPServer
from pathlib import Path

import api_client
from api_server import OrderRequestHandler


class OrderApiTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.server = ThreadingHTTPServer(("127.0.0.1", 0), OrderRequestHandler)
        self.server.orders_file = Path(self.temp_dir.name) / "orders.csv"
        self.thread = threading.Thread(target=self.server.serve_forever)
        self.thread.start()
        self.original_api_url = api_client.API_URL
        api_client.API_URL = f"http://127.0.0.1:{self.server.server_port}"

    def tearDown(self):
        self.server.shutdown()
        self.thread.join()
        self.server.server_close()
        self.temp_dir.cleanup()
        api_client.API_URL = self.original_api_url

    def test_api_serves_menu_and_persists_orders_for_both_clients(self):
        menu = api_client.get_menu()
        self.assertIn("Mince Pie ($12)", menu["PIES"])
        self.assertIn("OTHER DESSERTS", menu)
        self.assertIn("Turkey Pot Pie ($12)", menu["PIES"])
        self.assertIn("APPETIZERS", menu)

        order = api_client.submit_order(
            "Casey",
            [{"category": "PIES", "item": "Mince Pie ($12)"}],
        )

        self.assertEqual(order["customer_name"], "Casey")
        self.assertEqual(api_client.get_orders(), [order])

    def test_api_rejects_items_not_in_the_menu(self):
        with self.assertRaisesRegex(RuntimeError, "HTTP 400"):
            api_client.submit_order(
                "Casey",
                [{"category": "PIES", "item": "Not on the menu"}],
            )
        self.assertEqual(api_client.get_orders(), [])

    def test_api_persists_drink_addons(self):
        order = api_client.submit_order(
            "Casey",
            [
                {
                    "category": "DRINKS",
                    "item": "Tea ($2)",
                    "addons": ["milk", "sugar"],
                }
            ],
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
        self.assertEqual(api_client.get_orders(), [order])


if __name__ == "__main__":
    unittest.main()
