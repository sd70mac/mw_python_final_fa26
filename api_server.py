"""Local HTTP API shared by the console and Streamlit applications."""

import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

from restaurant import ORDERS_FILE, create_order, load_menu, read_orders


HOST = "127.0.0.1"
PORT = 8000


class OrderRequestHandler(BaseHTTPRequestHandler):
    def _orders_file(self):
        return getattr(self.server, "orders_file", ORDERS_FILE)

    def _send_json(self, status, payload):
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        if self.path == "/menu":
            try:
                self._send_json(200, load_menu())
            except (OSError, ValueError) as error:
                self._send_json(500, {"error": str(error)})
        elif self.path == "/orders":
            try:
                self._send_json(200, read_orders(self._orders_file()))
            except (OSError, ValueError, KeyError) as error:
                self._send_json(500, {"error": str(error)})
        else:
            self._send_json(404, {"error": "Endpoint not found."})

    def do_POST(self):
        if self.path != "/orders":
            self._send_json(404, {"error": "Endpoint not found."})
            return

        try:
            content_length = int(self.headers.get("Content-Length", "0"))
            if content_length <= 0 or content_length > 1_000_000:
                raise ValueError("Request body must be between 1 byte and 1 MB.")
            payload = json.loads(self.rfile.read(content_length).decode("utf-8"))
            if not isinstance(payload, dict):
                raise ValueError("Request body must be a JSON object.")
            order = create_order(
                payload.get("customer_name", ""),
                payload.get("items", []),
                load_menu(),
                orders_file=self._orders_file(),
            )
        except (UnicodeDecodeError, json.JSONDecodeError, TypeError, ValueError) as error:
            self._send_json(400, {"error": str(error)})
            return
        except (OSError, KeyError) as error:
            self._send_json(500, {"error": str(error)})
            return

        self._send_json(201, order)

    def log_message(self, format_string, *args):
        print(f"[order-api] {self.address_string()} - {format_string % args}")


def main():
    server = ThreadingHTTPServer((HOST, PORT), OrderRequestHandler)
    server.orders_file = ORDERS_FILE
    print(f"Pie in the Sky order service listening at http://{HOST}:{PORT}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopping the order service.")
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
