import json
import unittest
from unittest.mock import patch

import api_client


class FakeResponse:
    def __init__(self, value):
        self.body = json.dumps(value).encode("utf-8")

    def __enter__(self):
        return self

    def __exit__(self, *_):
        return None

    def read(self):
        return self.body


class SupabaseClientTests(unittest.TestCase):
    def setUp(self):
        self.original_url = api_client._SUPABASE_URL
        self.original_key = api_client._SUPABASE_KEY
        api_client.configure_supabase(
            "https://restaurant-test.supabase.co",
            "sb_secret_test-key",
        )

    def tearDown(self):
        api_client._SUPABASE_URL = self.original_url
        api_client._SUPABASE_KEY = self.original_key

    @patch("api_client.urlopen")
    def test_get_menu_reads_repository_files_without_database_request(self, urlopen):
        menu = api_client.get_menu()

        self.assertIn("Mince Pie ($12)", menu["PIES"])
        self.assertIn("Cheddar Potato ($8)", menu["SOUPS"])
        urlopen.assert_not_called()

    @patch("api_client.urlopen")
    def test_submit_order_uses_authenticated_supabase_insert(self, urlopen):
        stored_order = {
            "order_id": "test-order-id",
            "timestamp": "2026-11-23T12:00:00+00:00",
            "customer_name": "Casey",
            "items": [{"category": "PIES", "item": "Mince Pie ($12)"}],
        }
        urlopen.return_value = FakeResponse([stored_order])

        result = api_client.submit_order(
            "Casey",
            [{"category": "PIES", "item": "Mince Pie ($12)"}],
        )

        request = urlopen.call_args.args[0]
        self.assertEqual(result, stored_order)
        self.assertEqual(request.method, "POST")
        self.assertEqual(
            request.get_header("Authorization"),
            "Bearer sb_secret_test-key",
        )
        self.assertTrue(request.full_url.endswith("/rest/v1/orders"))
        self.assertEqual(
            json.loads(request.data)["items"],
            [{"category": "PIES", "item": "Mince Pie ($12)"}],
        )

    @patch("api_client.urlopen")
    def test_get_orders_requests_recent_rows(self, urlopen):
        urlopen.return_value = FakeResponse([])

        self.assertEqual(api_client.get_orders(), [])
        request = urlopen.call_args.args[0]
        self.assertIn("order=timestamp.desc", request.full_url)
        self.assertIn("limit=20", request.full_url)

    @patch("api_client.urlopen")
    def test_unpriced_items_are_rejected_before_database_request(self, urlopen):
        with patch("api_client.load_menu", return_value={"PIES": ["Test Pie"]}):
            with self.assertRaisesRegex(ValueError, "does not have a price"):
                api_client.submit_order(
                    "Casey",
                    [{"category": "PIES", "item": "Test Pie"}],
                )
        urlopen.assert_not_called()

    def test_supabase_url_must_use_https(self):
        with self.assertRaisesRegex(ValueError, "HTTPS"):
            api_client.configure_supabase(
                "http://restaurant-test.supabase.co",
                "sb_secret_test-key",
            )


if __name__ == "__main__":
    unittest.main()
