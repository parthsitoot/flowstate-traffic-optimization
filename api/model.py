"""GET /api/model: held-out metrics for the actual trained Random Forest."""
from src.http_api import APIHandler

class handler(APIHandler):
    endpoint = 'model'
