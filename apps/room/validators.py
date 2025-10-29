from apps.models import Device

class DeviceValidator:
    """デバイス作成・更新用バリデータ"""
    def validate(self, data, owner_id, device_id=None):
        name = data.get('name')
        if not name:
            return False, 'Device name is required.'
        q = Device.query.filter_by(name=name, owner=owner_id)
        if device_id:
            q = q.filter(Device.id != device_id)
        if q.first():
            return False, 'Device name already exists.'
        return True, 'Validation passed.'
