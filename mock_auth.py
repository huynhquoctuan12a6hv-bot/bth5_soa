from http.server import BaseHTTPRequestHandler, HTTPServer


class AuthHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path != "/auth/verify":
            self.send_error(404)
            return

        authorization = self.headers.get("Authorization")
        if authorization != "Bearer demo-report-token":
            self.send_error(401)
            return

        self.send_response(200)
        self.end_headers()


if __name__ == "__main__":
    print("Mock Auth dang chay tai http://127.0.0.1:8001")
    HTTPServer(("127.0.0.1", 8001), AuthHandler).serve_forever()