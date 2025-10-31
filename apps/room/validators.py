from apps.models import Device


class DeviceValidator:
    """デバイス作成・更新用バリデータ"""

    def validate(self, data, owner_id):
        name = data.get("name")
        # Name is required
        if not name:
            return False, "Device name is required."
        # Name must be unique per user
        device = Device.query.filter_by(name=name, owner=owner_id).first()
        if device:
            return False, "Device name already exists."
        return True, "Validation passed."
