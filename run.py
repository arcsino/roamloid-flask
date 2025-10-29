from apps import create_app, settings
from apps.room.socketio import socketio
from flask_socketio import SocketIO


app = create_app()
# CORS_ORIGINSに基づいてCORS設定を適用
socketio.init_app(app, cors_allowed_origins=settings.CORS_ORIGINS, supports_credentials=True)
# socketio.init_app(app, cors_allowed_origins="*")

if __name__ == "__main__":
    socketio.run(app, host="0.0.0.0", port=5000, debug=True)
