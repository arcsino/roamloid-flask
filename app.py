from flask import render_template
from apps import create_app, settings
from apps.room.socketio import socketio
from flask_socketio import SocketIO


app = create_app()
socketio.init_app(app, cors_allowed_origins=settings.CORS_ORIGINS)
# socketio.init_app(app, cors_allowed_origins="*")


@app.route("/", methods=["GET"])
def health_page():
    return render_template("index.html")


if __name__ == "__main__":
    socketio.run(app, host="0.0.0.0", port=5000, debug=True)
