from flask_socketio import SocketIO, disconnect, join_room, emit
from flask_login import current_user
from apps.models import db, Device, ChatMessage
from .gemini import convert_msg_into_command
import functools, json


socketio = SocketIO(async_mode="eventlet")


def authenticated_only(f):
    @functools.wraps(f)
    def wrapped(*args, **kwargs):
        if not current_user.is_authenticated:
            disconnect()
        else:
            return f(*args, **kwargs)

    return wrapped


@socketio.on("join_room")
@authenticated_only
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
    existing_device = Device.query.filter_by(in_3d=True, owner=user_id).first()
    if not existing_device:
        device.in_3d = True
        db.session.commit()
        existing_device = Device.query.filter_by(in_3d=True, owner=user_id).first()
    join_room(user_id)
    emit(
        "joined",
        {
            "device_name": device_name,
            "is_ai_here": device.in_3d,
            "ai_location": existing_device.name,
        },
    )


@socketio.on("send_data")
@authenticated_only
def handle_send_data(data):
    user_id = current_user.id
    device_name = data.get("device_name")
    msg = data.get("msg")
    msg_and_from = str({"msg": msg, "from": device_name})

    # saving chat message to database
    if msg is None or msg == "":
        emit("error", {"msg": "message is required."})
        return
    else:
        # 新しい順で5件取得
        past_messages = list(
            ChatMessage.query.filter_by(user_id=user_id)
            .order_by(ChatMessage.timestamp.desc())
            .limit(5)
            .all()
        )
        past_messages = [
            {"msg": pm.text, "response": pm.command} for pm in past_messages
        ]
        converted_msg, status_code = convert_msg_into_command(
            msg_and_from, past_messages
        )
        if status_code != 200:
            emit("error", {"msg": converted_msg})
            return
        else:
            print("Converted message:", converted_msg)
        chat_message = ChatMessage(
            user_id=user_id,
            device_id=Device.query.filter_by(name=device_name, owner=user_id)
            .first()
            .id,
            text=msg,
            command=converted_msg,
        )
        db.session.add(chat_message)
        db.session.commit()

    # Emit response based on command
    command_json = json.loads(converted_msg)
    # action: conversation
    if command_json.get("action") == "conversation":
        try:
            response = command_json.get("response", "")
            emit(
                "receive_data",
                {
                    "msg": msg,
                    "text": response,
                    "device_name": device_name,
                },
                room=user_id,
            )
        except Exception as e:
            emit("error", {"msg": str(e)})
    # action: move
    if command_json.get("action") == "move":
        try:
            to_device_name = command_json.get("to_device_name")
            response = command_json.get("response", "")
            # set all Devices' in_3d to False for the user
            Device.query.filter_by(owner=user_id).update({"in_3d": False})
            # set only the target Device's in_3d to True
            to_device = Device.query.filter_by(
                name=to_device_name, owner=user_id
            ).first()
            if to_device:
                to_device.in_3d = True
                db.session.commit()
                emit(
                    "moved_3d",
                    {
                        "to_device_name": to_device_name,
                        "msg": msg,
                        "text": response,
                        "device_name": device_name,
                    },
                    room=user_id,
                )
        except Exception as e:
            emit("error", {"msg": str(e)})
    # action: animation
    if command_json.get("action") == "animation":
        try:
            animation_type = command_json.get("animation_type")
            response = command_json.get("response", "")
            emit(
                "receive_data",
                {
                    "action": "animation",
                    "animation_type": animation_type,
                    "msg": msg,
                    "text": response,
                    "device_name": device_name,
                },
                room=user_id,
            )
        except Exception as e:
            emit("error", {"msg": str(e)})
