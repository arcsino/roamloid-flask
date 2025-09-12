from flask import request
from flask_restful import Resource


class HealthCheckResource(Resource):
    """Health check resource."""

    def get(self):
        return {"status": "ok"}, 200  # OK
