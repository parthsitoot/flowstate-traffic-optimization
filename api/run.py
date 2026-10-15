"""GET /api/run?scenario=rush&seed=42: compare three controllers."""
from src.http_api import APIHandler

class handler(APIHandler):
    endpoint = 'run'
