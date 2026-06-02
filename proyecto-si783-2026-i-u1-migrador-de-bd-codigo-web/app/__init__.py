import os

from flask import Flask
from flask_socketio import SocketIO
from flask_mail import Mail
import traceback

socketio = SocketIO()
mail = Mail()

def crear_app():
    app = Flask(__name__)

    # Cargar configuración
    from config import Config
    app.config.from_object(Config)

    async_mode = os.environ.get('SOCKETIO_ASYNC_MODE')
    if async_mode is None and os.name == 'nt':
        async_mode = 'threading'
    socketio.init_app(app, cors_allowed_origins="*", async_mode=async_mode)
    mail.init_app(app)

    # Configurar OAuth
    from app.oauth import configurar_oauth
    configurar_oauth(app)

    from app.routes import principal
    app.register_blueprint(principal)

    # Manejador global de errores para devolver JSON en lugar de HTML
    @app.errorhandler(Exception)
    def manejar_error(error):
        """Devuelve errores como JSON para evitar que el cliente reciba HTML con <!doctype"""
        from flask import jsonify
        print(f'[ERROR GLOBAL] {str(error)}')
        traceback.print_exc()
        return jsonify({'estado': 'error', 'mensaje': f'Error del servidor: {str(error)}'}), 500

    return app