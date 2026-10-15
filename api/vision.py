"""GET /api/vision?q=1,2,3,4: process a synthetic frame and return boxes."""
from src.http_api import APIHandler

class handler(APIHandler):
    endpoint = 'vision'
