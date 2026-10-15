"""GET /api/predict?counts=6,6,6: run user inputs through the fitted forest."""
from src.http_api import APIHandler

class handler(APIHandler):
    endpoint = 'predict'
