"""GET /api/predict?counts=6,6,6: compare three fitted arrival forecasters."""
from src.http_api import APIHandler

class handler(APIHandler):
    endpoint = 'predict'
