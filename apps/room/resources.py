from flask import request
from flask_restful import Resource
from flask_login import login_required, current_user
from apps.models import db, Device
from .validators import DeviceValidator


class DeviceListCreateResource(Resource):
    """Device list retrieval and creation API"""

    validator = DeviceValidator()

    @login_required
    def get(self):
        devices = Device.query.filter_by(owner=current_user.id).all()
        device_list = [{"id": d.id, "name": d.name, "in_3d": d.in_3d} for d in devices]
        return {"devices": device_list}, 200

    @login_required
    def post(self):
        data = request.get_json()
        # Validation
        is_valid, message = self.validator.validate(data, current_user.id)
        if not is_valid:
            return {"error_message": message}, 400
        # Create new device
        name = data.get("name")
        new_device = Device(name=name, owner=current_user.id)
        db.session.add(new_device)
        db.session.commit()
        return {
            "id": new_device.id,
            "name": new_device.name,
            "in_3d": new_device.in_3d,
        }, 201


class DeviceRetrieveUpdateDestroyResource(Resource):
    """Device detail, update, and delete API"""

    validator = DeviceValidator()

    @login_required
    def get(self, device_id):
        device = Device.query.filter_by(id=device_id, owner=current_user.id).first()
        if not device:
            return {"error_message": "Device not found."}, 404
        return {"id": device.id, "name": device.name, "in_3d": device.in_3d}, 200

    @login_required
    def put(self, device_id):
        data = request.get_json()
        # Validation
        is_valid, message = self.validator.validate(data, current_user.id)
        if not is_valid:
            return {"error_message": message}, 400
        # Update device
        name = data.get("name")
        device = Device.query.filter_by(id=device_id, owner=current_user.id).first()
        if not device:
            return {"error_message": "Device not found."}, 404
        device.name = name
        db.session.commit()
        return {"id": device.id, "name": device.name, "in_3d": device.in_3d}, 200

    @login_required
    def delete(self, device_id):
        device = Device.query.filter_by(id=device_id, owner=current_user.id).first()
        if not device:
            return {"error_message": "Device not found."}, 404
        db.session.delete(device)
        db.session.commit()
        return {"message": "Device deleted successfully."}, 200
