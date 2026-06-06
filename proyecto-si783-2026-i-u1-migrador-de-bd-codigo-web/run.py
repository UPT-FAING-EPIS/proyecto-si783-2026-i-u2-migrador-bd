from app import crear_app, socketio
import os

try:
    app = crear_app()
    print("App created successfully")
except Exception as e:
    print(f"Error creating app: {e}")
    raise

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    host = os.environ.get("HOST", "127.0.0.1")
    print(f"Iniciando servidor en {host}:{port}")
    socketio.run(app, host=host, port=port, debug=False, use_reloader=False, allow_unsafe_werkzeug=True)