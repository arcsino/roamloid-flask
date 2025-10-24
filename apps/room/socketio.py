from flask_socketio import SocketIO, join_room, emit
from flask_login import login_required, current_user
from apps.models import db, Device, ChatMessage


socketio = SocketIO()


@login_required
@socketio.on("join_room")
def handle_join_room(data):
    user_id = current_user.id
    device_name = data.get("device_name")

    # Validate input
    if not user_id or not device_name:
        emit("error", {"msg": "user_id and device_name required."})
        return
    # if not existing device, create new one
    device = Device.query.filter_by(name=device_name, owner=user_id).first()
    if not device:
        device = Device(name=device_name, owner=user_id)
        db.session.add(device)
        db.session.commit()
    join_room(user_id)
    emit("joined", {"device_name": device_name})


@login_required
@socketio.on("send_data")
def handle_send_data(data):
    user_id = current_user.id
    device_name = data.get("device_name")
    msg = data.get("msg")
    move = data.get("move")  # example: {'to_device_name': ...

    # saving chat message to database
    if msg is None:
        emit("error", {"msg": "message is required."})
        return
    else:
        chat_message = ChatMessage(
            user_id=user_id,
            device_id=Device.query.filter_by(name=device_name, owner=user_id)
            .first()
            .id,
            text=msg,
        )
        db.session.add(chat_message)
        db.session.commit()
    # handling 3D movement
    if move:
        to_device_name = move.get("to_device_name")
        # set all Devices' in_3d to False for the user
        Device.query.filter_by(owner=user_id).update({"in_3d": False})
        # set only the target Device's in_3d to True
        to_device = Device.query.filter_by(name=to_device_name, owner=user_id).first()
        if to_device:
            to_device.in_3d = True
            db.session.commit()
            emit("moved_3d", {"to_device_name": to_device_name}, room=user_id)
    emit("receive_data", {"device_name": device_name, "text": msg}, room=user_id)
