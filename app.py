"""Local entry point. Run python3 app.py and open http://localhost:8000.
Vercel uses api/*.py instead; both paths call src/service.py.
"""
import json
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from pathlib import Path
from urllib.parse import urlparse, parse_qs
from src.service import response_for

ROOT = Path(__file__).parent

class Handler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(ROOT / 'web'), **kwargs)

    def do_GET(self):
        url = urlparse(self.path)
        if not url.path.startswith('/api/'):
            return super().do_GET()
        status, data = response_for(url.path.removeprefix('/api/'), parse_qs(url.query, keep_blank_values=True))
        body = json.dumps(data).encode('utf-8')
        self.send_response(status)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.send_header('Cache-Control', 'no-store')
        self.send_header('Content-Length', str(len(body)))
        self.end_headers()
        self.wfile.write(body)

if __name__ == '__main__':
    server = ThreadingHTTPServer(('127.0.0.1', 8000), Handler)
    print('FlowState ready: http://localhost:8000', flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        server.server_close()
