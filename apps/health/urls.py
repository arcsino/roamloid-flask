from flask_restful import Api
from .resources import HealthCheckResource


health_api = Api(prefix="/api/health")
health_api.add_resource(HealthCheckResource, "/")
