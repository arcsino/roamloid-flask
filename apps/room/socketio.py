from flask_socketio import SocketIO, join_room, emit
from flask_login import login_required, current_user
from apps.models import db, Device, ChatMessage


socketio = SocketIO()


@login_required
@socketio.on("join_room")
def handle_join_room(data):
    user_id = current_user.id #ここでclient.jsが送ってきたクッキーをチェックして、ログインしているユーザーのIDを取得
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
    
    # --- gemini APIからのコマンドを受け取るコードのテスト用コード ---
    # このユーザーが他にin_3d=Trueのデバイスを持っていないか確認
    existing_3d_device = Device.query.filter_by(owner=user_id, in_3d=True).first()
    if not existing_3d_device:
        # 誰もいなければ、このデバイスをAIの初期位置(in_3d=True)にする
        device.in_3d = True
        db.session.commit()
        print(f"!!! テスト用: {device_name} をAIの初期位置に設定しました。")
    # ------------------------------------------------------

    join_room(user_id)

    # "joined" イベントでクライアントに現在の状態を送信
    emit("joined", {
        "device_name": device.name,
        "is_ai_here": device.in_3d,# device.in_3d は、DBから取ってきた最新の状態 (True or False) 
        "ai_location": existing_3d_device.name if existing_3d_device else "None"# AIがどこにいるか
    })


@login_required
@socketio.on("send_data")
def handle_send_data(data):
    user_id = current_user.id
    device_name = data.get("device_name") # デバイス名
    msg = data.get("msg") # ユーザーからのチャットメッセージ
    # move = data.get("move")  # 移動指示はAIから貰うので、クライアントのmoveは消去

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
    
# --- ↓↓ Gemini APIの「フリ」をする ↓↓ ---
    
    # 1. AIが「今」どこにいるか調べる (例: "saba1")
    ai_device = Device.query.filter_by(owner=user_id, in_3d=True).first()
    ai_device_name = ai_device.name if ai_device else "None" 

    # 2. ユーザーがメッセージを送ってきたデバイス名（＝移動先）
    to_device_name = device_name # (例: "saba2")

    # 3. ダミーのGemini返信を組み立てる
    chat_reply = f"{to_device_name} に移動しますね！"
    gemini_command = f"command:{ai_device_name}から{to_device_name}へ移動"
    # --- ↑↑ ここまでが「フリ」 ↑↑ ---


    # handling 3D movement
    if gemini_command: # ← ダミーのコマンドで必ずTrueになります
        
        # ↓↓↓ この移動処理はマスターのコードとほぼ同じです ↓↓↓
        Device.query.filter_by(owner=user_id).update({"in_3d": False})
        to_device = Device.query.filter_by(name=to_device_name, owner=user_id).first()
        
        if to_device:
            to_device.in_3d = True
            db.session.commit()
            # "moved_3d" を全員に通知！
            emit("moved_3d", {"to_device_name": to_device_name}, room=user_id)

    # 最後にダミーの「返信」をみんなに送る
    emit("receive_data", {"device_name": "AI", "text": chat_reply}, room=user_id)
# --- ↑↑ Gemini APIの「フリ」をする ↑↑ ---


    # gemini APIからのコマンドを受け取る
    # 1. AIが今どこにいるか調べる(in_3d=True のデバイスを探す)
    ai_device = Device.query.filter_by(owner=user_id, in_3d=True).first()
    ai_device_name = ai_device.name if ai_device else "None" # (例: 端末1)
    
    # 2. Gemini用のプロンプト
    prompt = f"""
    あなたは高性能AIです。
    利用可能な端末は {user_id} の {Device.query.filter_by(owner=user_id).all()} です。
    あなたは今「{ai_device_name}」にいます。
    ユーザーは「{device_name}」から「{msg}」と送ってきました。
    チャットへの返答と、必要なら移動コマンド(command: [移動元]から[移動先]へ移動)を生成してください。
    """
    
    # 3. Gemini APIを呼び出す（ここはあとで別途実装）
    # gemini_response = call_gemini_api(prompt)
    gemini_response = "承知しました、そちらへ向かいます。 command:端末1から端末2へ移動" # (ダミーのレスポンス)

    # 4. Geminiの返事を解析する
    chat_reply = gemini_response.split(" command:")[0] # (例: 承知しました、そちらへ向かいます。)
    move_command = gemini_response.split(" command:")[-1] if " command:" in gemini_response else None

    # 5. もし移動コマンド(command:)が返ってきたら…
    if move_command and "から" in move_command and "へ移動" in move_command:
        # (move_command を解析して "端末2" (to_device_name) を取り出す処理)
        to_device_name = "端末2" # (ダミー)

        # set all Devices' in_3d to False for the user
        Device.query.filter_by(owner=user_id).update({"in_3d": False})
        # set only the target Device's in_3d to True
        to_device = Device.query.filter_by(name=to_device_name, owner=user_id).first()
        if to_device:
            to_device.in_3d = True
            db.session.commit()
            # "moved_3d" を全員に通知
            emit("moved_3d", {"to_device_name": to_device_name}, room=user_id)

    # 6. Geminiの「チャット返信」を全員に送る
    # emit("receive_data", {"device_name": "AI", "text": chat_reply}, room=user_id)
