from flask_restful import Api
from .resources import DeviceListResource, DeviceResource

room_api = Api(prefix="/api/room")
room_api.add_resource(DeviceListResource, "/devices")
room_api.add_resource(DeviceResource, "/devices/<string:device_id>")
