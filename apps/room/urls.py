from flask_restful import Api
from .resources import DeviceListCreateResource, DeviceResource

room_api = Api(prefix="/api/room")
room_api.add_resource(DeviceListCreateResource, "/devices")
room_api.add_resource(DeviceResource, "/devices/<string:device_id>")
