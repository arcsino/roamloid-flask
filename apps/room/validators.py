from apps.models import Device


class DeviceValidator:
    """デバイス作成・更新用バリデータ"""

    def validate(self, data, owner_id, device_id=None):
        name = data.get("name")
        if not name:
            return False, "Device name is required."
        device = Device.query.filter_by(name=name, owner=owner_id).first()
        if device_id:
            if device and device.id != device_id:
                return False, "Device name already exists."
        else:
            if device:
                return False, "Device name already exists."
        return True, "Validation passed."
