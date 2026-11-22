import json
from http.server import BaseHTTPRequestHandler, HTTPServer


class OrderHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path != "/orders/101":
            self.send_error(404)
            return

        order = {
            "id": 101,
            "items": [
                {
                    "product_id": 7,
                    "quantity": 3,
                    "unit_price": "150000.00",
                    "unit_cost": "100000.00",
                }
            ],
        }
        body = json.dumps(order).encode("utf-8")

        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)


if __name__ == "__main__":
    print("Mock Orders dang chay tai http://127.0.0.1:8002")
    HTTPServer(("127.0.0.1", 8002), OrderHandler).serve_forever()