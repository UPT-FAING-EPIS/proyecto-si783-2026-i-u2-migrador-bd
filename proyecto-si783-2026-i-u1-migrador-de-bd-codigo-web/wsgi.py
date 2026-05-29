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
    socketio.run(app, host='0.0.0.0', port=port, debug=False, use_reloader=False)