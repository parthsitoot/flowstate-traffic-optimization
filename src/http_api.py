"""Small adapter between Vercel HTTP requests and the shared service."""
import json
from http.server import BaseHTTPRequestHandler
from urllib.parse import parse_qs, urlparse
from .service import response_for

class APIHandler(BaseHTTPRequestHandler):
    endpoint = ''

    def do_GET(self):
        status, data = response_for(self.endpoint, parse_qs(urlparse(self.path).query, keep_blank_values=True))
        body = json.dumps(data).encode('utf-8')
        self.send_response(status)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.send_header('Cache-Control', 'no-store')
        self.send_header('Content-Length', str(len(body)))
        self.end_headers()
        self.wfile.write(body)
