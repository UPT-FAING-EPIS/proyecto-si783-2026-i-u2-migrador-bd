from flask import Blueprint, render_template, request, jsonify, send_file, session, redirect, url_for
from app import socketio
import os
import base64
import requests
from werkzeug.utils import secure_filename
from datetime import datetime
import tempfile
import zipfile
import json
import sqlite3

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from utilidades.detector import DetectorBaseDatos
from extraccion.conector import ConectorOrigen
from transformacion.mapeador import MapeadorDatos
from carga.cargador import CargadorDestino
from app.auth import (
    inicializar_bd, verificar_usuario, registrar_usuario, requerir_login,
    requerir_admin, obtener_usuario_actual, crear_nuevo_admin, DB_PATH,
    registrar_usuario_oauth, verificar_codigo, enviar_email_notificacion
)

principal = Blueprint('principal', __name__)

# Inicializar base de datos de autenticación
inicializar_bd()

# Corregir ruta de uploads
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'uploads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


def _carpeta_upload_usuario() -> str:
    """Devuelve la carpeta de uploads aislada para el usuario actual."""
    usuario_id = session.get('usuario_id')
    usuario = session.get('usuario', 'anonimo')
    identificador = f'user_{usuario_id}' if usuario_id is not None else secure_filename(usuario) or 'anonimo'
    ruta = os.path.join(UPLOAD_FOLDER, identificador)
    os.makedirs(ruta, exist_ok=True)
    return ruta

estado_app = {
    'origen': None,
    'destino': None,
    'proceso_activo': False,
    'metricas': {'extraidos': 0, 'cargados': 0, 'errores': 0, 'tablas_ok': 0},
    'historial': [],   # registros de migraciones completadas
    'logs': [],        # log detallado de todas las acciones
    'ips': [],         # registro de accesos por IP
}

def _registrar_log(mensaje: str, tipo: str = 'info', ip: str = None):
    """Agrega entrada al log detallado de la aplicacion."""
    entrada = {
        'fecha': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'tipo': tipo,
        'mensaje': mensaje,
        'ip': ip or '',
    }
    estado_app['logs'].append(entrada)
    socketio.emit('log', {'mensaje': mensaje, 'tipo': tipo}, skip_sid=None)

MAX_IPS = 1000  # limite para evitar crecimiento ilimitado de memoria

def _registrar_ip(ip: str, actividad: str, usuario: str = None):
    """Registra acceso de una IP. Si ya existe, actualiza fecha/hora/actividad."""
    ahora = datetime.now()
    fecha = ahora.strftime('%Y-%m-%d')
    hora = ahora.strftime('%H:%M:%S')
    
    # Buscar si esta IP ya existe
    ip_existente = None
    for entrada in estado_app['ips']:
        if entrada['ip'] == ip:
            ip_existente = entrada
            break
    
    if ip_existente:
        # Actualizar fecha, hora, actividad y usuario si cambia
        ip_existente['fecha'] = fecha
        ip_existente['hora'] = hora
        ip_existente['actividad'] = actividad
        ip_existente['usuario'] = usuario or ip_existente.get('usuario', 'anónimo')
        ip_existente['accesos'] = ip_existente.get('accesos', 1) + 1
    else:
        # Nueva IP: agregar
        if len(estado_app['ips']) >= MAX_IPS:
            estado_app['ips'].pop(0)
        estado_app['ips'].append({
            'ip': ip,
            'fecha': fecha,
            'hora': hora,
            'actividad': actividad,
            'usuario': usuario or 'anónimo',
            'accesos': 1
        })

def _registrar_actividad_ip(actividad_desc: str):
    """Registra actividad real de una IP (no navegaciones)."""
    ip = request.remote_addr or 'desconocida'
    usuario = session.get('usuario', 'anónimo')
    _registrar_ip(ip, actividad_desc, usuario)


def _resumen_origen_detectado(tipo: str, mensaje: str = '') -> dict:
    """Normaliza la salida de detección para mostrar el motor de origen sin ambigüedad."""
    return {
        'tipo_detectado': tipo,
        'motor_origen': tipo,
        'mensaje_deteccion': mensaje or '',
    }

# ==================== RUTAS DE AUTENTICACIÓN ====================

@principal.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        usuario = request.form.get('usuario')
        contraseña = request.form.get('contraseña')

        usuario_data = verificar_usuario(usuario, contraseña)
        if usuario_data:
            session['usuario_id'] = usuario_data['id']
            session['usuario'] = usuario_data['usuario']
            session['rol'] = usuario_data['rol']
            _registrar_log(f'Usuario {usuario} iniciado sesión', 'info', request.remote_addr)
            return redirect(url_for('principal.migracion'))
        else:
            # Verificar si el usuario existe pero no está verificado
            from app.auth import obtener_usuario_por_email
            # Asumir que usuario podría ser email o nombre, pero para simplificar, buscar por usuario
            # Para mejor UX, podríamos buscar por email también
            return render_template('login.html', error='Usuario o contraseña incorrectos, o cuenta no verificada. Revisa tu email.')

    error = request.args.get('error')
    mensaje = request.args.get('mensaje')
    return render_template('login.html', error=error, mensaje=mensaje)

@principal.route('/registro', methods=['GET', 'POST'])
def registro():
    if request.method == 'POST':
        usuario = request.form.get('usuario')
        email = request.form.get('email')
        contraseña = request.form.get('contraseña')
        confirmar = request.form.get('confirmar')

        if contraseña != confirmar:
            return render_template('registro.html', error='Las contraseñas no coinciden')

        if len(contraseña) < 6:
            return render_template('registro.html', error='La contraseña debe tener mínimo 6 caracteres')

        if len(usuario) < 3:
            return render_template('registro.html', error='El usuario debe tener mínimo 3 caracteres')

        exito, mensaje = registrar_usuario(usuario, email, contraseña)
        if exito:
            _registrar_log(f'Nuevo usuario registrado: {usuario}', 'info', request.remote_addr)
            return render_template('verificar.html', email=email, mensaje=mensaje)
        else:
            return render_template('registro.html', error=mensaje)

    error = request.args.get('error')
    return render_template('registro.html', error=error)

@principal.route('/verificar', methods=['GET', 'POST'])
def verificar():
    if request.method == 'POST':
        email = request.form.get('email')
        codigo = request.form.get('codigo')

        exito, mensaje = verificar_codigo(email, codigo)
        if exito:
            _registrar_log(f'Usuario verificado: {email}', 'info', request.remote_addr)
            return render_template('login.html', mensaje=mensaje + ' Ahora puedes iniciar sesión.')
        else:
            return render_template('verificar.html', email=email, error=mensaje)

    email = request.args.get('email')
    return render_template('verificar.html', email=email)

@principal.route('/logout')
def logout():
    usuario = session.get('usuario', 'desconocido')
    session.clear()
    _registrar_log(f'Usuario {usuario} cerró sesión', 'info', request.remote_addr)
    return redirect(url_for('principal.login'))

# ==================== RUTAS OAUTH ====================

@principal.route('/auth/<proveedor>')
def oauth_login(proveedor):
    """Inicia el flujo de login OAuth con Google o GitHub."""
    action = request.args.get('action', 'login')
    session['oauth_action'] = action
    
    if proveedor.lower() == 'google':
        from app.oauth import oauth
        redirect_uri = url_for('principal.oauth_callback', proveedor='google', _external=True)
        return oauth.google.authorize_redirect(redirect_uri)
    elif proveedor.lower() == 'github':
        from app.oauth import oauth
        redirect_uri = url_for('principal.oauth_callback', proveedor='github', _external=True)
        return oauth.github.authorize_redirect(redirect_uri)
    return redirect(url_for('principal.login'))

@principal.route('/auth/<proveedor>/callback')
def oauth_callback(proveedor):
    """Callback de OAuth."""
    try:
        from app.oauth import oauth
        action = session.pop('oauth_action', 'login')

        if proveedor.lower() == 'google':
            token = oauth.google.authorize_access_token()
            usuario_info = token.get('userinfo')

            if usuario_info:
                sub = usuario_info.get('sub')
                email = usuario_info.get('email')
                
                # Verificar si el usuario ya tiene cuenta registrada (por email o por OAuth previo)
                from app.auth import run_query
                oauth_existente = run_query('SELECT usuario_id FROM oauth_usuarios WHERE proveedor = ? AND proveedor_id = ?', ('google', sub), fetchone=True)
                usuario_existente = run_query('SELECT id FROM usuarios WHERE email = ?', (email,), fetchone=True)
                
                if action == 'login' and not oauth_existente and not usuario_existente:
                    return redirect(url_for('principal.login', error='No tienes una cuenta registrada. Regístrate primero con Google o GitHub.'))

                usuario_data = registrar_usuario_oauth(
                    proveedor='google',
                    proveedor_id=sub,
                    email=email,
                    nombre=usuario_info.get('name'),
                    foto_url=usuario_info.get('picture')
                )

                if usuario_data:
                    session['usuario_id'] = usuario_data['id']
                    session['usuario'] = usuario_data['usuario']
                    session['rol'] = usuario_data['rol']
                    _registrar_log(
                        f'Usuario {usuario_data["usuario"]} inició sesión con Google',
                        'info', request.remote_addr
                    )
                    return redirect(url_for('principal.migracion'))

        elif proveedor.lower() == 'github':
            token = oauth.github.authorize_access_token()
            session['github_access_token'] = token.get('access_token')
            session['github_token_type'] = token.get('token_type', 'bearer')

            # Obtener información del usuario de GitHub
            resp = oauth.github.get('user', token=token)
            usuario_info = resp.json()

            # Obtener email si no está en el perfil público
            email = usuario_info.get('email')
            if not email:
                resp_email = oauth.github.get('user/emails', token=token)
                emails = resp_email.json()
                for e in emails:
                    if e.get('primary'):
                        email = e.get('email')
                        break
                if not email and emails:
                    email = emails[0].get('email')

            if email:
                sub = str(usuario_info.get('id'))
                
                # Verificar si el usuario ya tiene cuenta registrada (por email o por OAuth previo)
                from app.auth import run_query
                oauth_existente = run_query('SELECT usuario_id FROM oauth_usuarios WHERE proveedor = ? AND proveedor_id = ?', ('github', sub), fetchone=True)
                usuario_existente = run_query('SELECT id FROM usuarios WHERE email = ?', (email,), fetchone=True)
                
                if action == 'login' and not oauth_existente and not usuario_existente:
                    return redirect(url_for('principal.login', error='No tienes una cuenta registrada. Regístrate primero con Google o GitHub.'))

                usuario_data = registrar_usuario_oauth(
                    proveedor='github',
                    proveedor_id=sub,
                    email=email,
                    nombre=usuario_info.get('name') or usuario_info.get('login'),
                    foto_url=usuario_info.get('avatar_url')
                )

                if usuario_data:
                    session['usuario_id'] = usuario_data['id']
                    session['usuario'] = usuario_data['usuario']
                    session['rol'] = usuario_data['rol']
                    _registrar_log(
                        f'Usuario {usuario_data["usuario"]} inició sesión con GitHub',
                        'info', request.remote_addr
                    )
                    return redirect(url_for('principal.migracion'))
            else:
                return redirect(url_for('principal.login', error='No se pudo obtener el email de GitHub'))

        return redirect(url_for('principal.login', error='Error en autenticación OAuth'))

    except Exception as e:
        _registrar_log(f'Error OAuth {proveedor}: {str(e)}', 'error', request.remote_addr)
        return redirect(url_for('principal.login', error=f'Error: {str(e)}'))


def _github_token_actual():
    """Devuelve el access token de GitHub asociado a la sesión actual."""
    return session.get('github_access_token')


def _github_headers():
    token = _github_token_actual()
    if not token:
        return None
    return {
        'Authorization': f'Bearer {token}',
        'Accept': 'application/vnd.github+json',
        'X-GitHub-Api-Version': '2022-11-28'
    }


@principal.route('/api/github/repos', methods=['GET'])
@requerir_login
def api_github_repos():
    """Lista los repositorios visibles para el usuario de GitHub autenticado."""
    headers = _github_headers()
    if not headers:
        return jsonify({'estado': 'error', 'mensaje': 'Primero conecta tu cuenta de GitHub desde /auth/github'}), 401

    try:
        url = 'https://api.github.com/user/repos?per_page=100&sort=updated&direction=desc'
        respuesta = requests.get(url, headers=headers, timeout=20)
        if respuesta.status_code != 200:
            return jsonify({'estado': 'error', 'mensaje': f'GitHub respondió {respuesta.status_code}: {respuesta.text}'}), 400

        datos = respuesta.json()
        repos = []
        for repo in datos:
            repos.append({
                'id': repo.get('id'),
                'name': repo.get('name'),
                'full_name': repo.get('full_name'),
                'private': repo.get('private', False),
                'html_url': repo.get('html_url'),
                'default_branch': repo.get('default_branch', 'main'),
                'description': repo.get('description') or ''
            })

        return jsonify({'estado': 'exito', 'repos': repos})
    except Exception as e:
        return jsonify({'estado': 'error', 'mensaje': f'No se pudieron listar repositorios: {str(e)}'}), 500


@principal.route('/api/github/crear-repo', methods=['POST'])
@requerir_login
def api_github_crear_repo():
    """Crea un repositorio nuevo en la cuenta GitHub del usuario autenticado."""
    headers = _github_headers()
    if not headers:
        return jsonify({'estado': 'error', 'mensaje': 'Conecta tu cuenta de GitHub primero'}), 401

    datos = request.json or {}
    nombre = (datos.get('nombre') or '').strip()
    descripcion = (datos.get('descripcion') or '').strip()
    privado_raw = datos.get('privado', True)
    if isinstance(privado_raw, bool):
        privado = privado_raw
    else:
        privado = str(privado_raw).strip().lower() not in ('publico', 'public', 'false', '0', 'no')

    if not nombre:
        return jsonify({'estado': 'error', 'mensaje': 'Debes indicar un nombre de repositorio'}), 400

    try:
        payload = {
            'name': nombre,
            'description': descripcion,
            'private': privado,
            'auto_init': True
        }
        respuesta = requests.post('https://api.github.com/user/repos', headers=headers, json=payload, timeout=30)

        if respuesta.status_code not in (200, 201):
            return jsonify({'estado': 'error', 'mensaje': f'GitHub respondió {respuesta.status_code}: {respuesta.text}'}), 400

        repo = respuesta.json()

        # Crear una carpeta inicial con un archivo marcador para que el repo no quede vacío.
        branch = repo.get('default_branch', 'main')
        carpeta_inicial = 'migraciones'
        marcador_path = f'{carpeta_inicial}/.gitkeep'
        marcador_payload = {
            'message': 'Crear carpeta inicial migraciones',
            'content': base64.b64encode(b'').decode('utf-8'),
            'branch': branch
        }
        requests.put(
            f'https://api.github.com/repos/{repo.get("full_name")}/contents/{marcador_path}',
            headers=headers,
            json=marcador_payload,
            timeout=30
        )

        _registrar_log(f'Repositorio GitHub creado: {repo.get("full_name")}', 'info', request.remote_addr)
        return jsonify({
            'estado': 'exito',
            'mensaje': 'Repositorio creado correctamente',
            'repo': {
                'id': repo.get('id'),
                'name': repo.get('name'),
                'full_name': repo.get('full_name'),
                'private': repo.get('private', False),
                'html_url': repo.get('html_url'),
                'default_branch': repo.get('default_branch', 'main'),
                'description': repo.get('description') or '',
                'initial_folder': carpeta_inicial
            }
        })
    except Exception as e:
        _registrar_log(f'Error creando repositorio GitHub: {str(e)}', 'error', request.remote_addr)
        return jsonify({'estado': 'error', 'mensaje': f'Error creando repositorio: {str(e)}'}), 500


@principal.route('/api/github/archivos-locales', methods=['GET'])
@requerir_login
def api_github_archivos_locales():
    """Lista archivos del usuario actual para elegir cuál subir."""
    try:
        carpeta_usuario = _carpeta_upload_usuario()
        archivos = []
        for nombre in sorted(os.listdir(carpeta_usuario)):
            ruta = os.path.join(carpeta_usuario, nombre)
            if os.path.isfile(ruta):
                archivos.append({
                    'nombre': nombre,
                    'tamano': os.path.getsize(ruta),
                    'ruta_relativa': os.path.join(os.path.basename(carpeta_usuario), nombre)
                })
        return jsonify({'estado': 'exito', 'archivos': archivos})
    except Exception as e:
        return jsonify({'estado': 'error', 'mensaje': str(e)}), 500


@principal.route('/api/github/subir', methods=['POST'])
@requerir_login
def api_github_subir():
    """Sube un archivo desde uploads/ a un repositorio del usuario en GitHub."""
    headers = _github_headers()
    if not headers:
        return jsonify({'estado': 'error', 'mensaje': 'Conecta tu cuenta de GitHub primero'}), 401

    datos = request.json or {}
    repo_full_name = datos.get('repo')
    archivo = datos.get('archivo')
    path_in_repo = datos.get('path') or archivo
    mensaje = datos.get('mensaje') or f'Subida desde MigradorBD: {archivo}'
    branch = datos.get('branch') or 'main'

    if not repo_full_name or not archivo:
        return jsonify({'estado': 'error', 'mensaje': 'Faltan repo o archivo'}), 400

    local_path = os.path.join(_carpeta_upload_usuario(), secure_filename(archivo))
    if not os.path.exists(local_path):
        return jsonify({'estado': 'error', 'mensaje': f'Archivo no encontrado: {archivo}'}), 404

    try:
        with open(local_path, 'rb') as f:
            contenido = f.read()

        contenido_b64 = base64.b64encode(contenido).decode('utf-8')
        api_url = f'https://api.github.com/repos/{repo_full_name}/contents/{path_in_repo}'

        # Ver si el archivo ya existe para actualizarlo
        sha = None
        get_resp = requests.get(api_url, headers=headers, params={'ref': branch}, timeout=20)
        if get_resp.status_code == 200:
            sha = get_resp.json().get('sha')

        payload = {
            'message': mensaje,
            'content': contenido_b64,
            'branch': branch
        }
        if sha:
            payload['sha'] = sha

        put_resp = requests.put(api_url, headers=headers, json=payload, timeout=30)
        if put_resp.status_code not in (200, 201):
            return jsonify({'estado': 'error', 'mensaje': f'GitHub respondió {put_resp.status_code}: {put_resp.text}'}), 400

        respuesta = put_resp.json()
        html_url = respuesta.get('content', {}).get('html_url')
        _registrar_log(f'Archivo {archivo} subido a GitHub en {repo_full_name}/{path_in_repo}', 'info', request.remote_addr)
        return jsonify({
            'estado': 'exito',
            'mensaje': 'Archivo subido correctamente a GitHub',
            'url': html_url,
            'repo': repo_full_name,
            'path': path_in_repo,
            'branch': branch
        })
    except Exception as e:
        _registrar_log(f'Error subiendo archivo a GitHub: {str(e)}', 'error', request.remote_addr)
        return jsonify({'estado': 'error', 'mensaje': f'Error subiendo archivo: {str(e)}'}), 500

@principal.route('/admin', methods=['GET', 'POST'])
@requerir_admin
def admin():
    usuario_actual = obtener_usuario_actual()
    if not usuario_actual:
        return redirect(url_for('principal.login'))

    error_admin = None
    exito_admin = None

    if request.method == 'POST':
        usuario_nuevo = request.form.get('usuario_nuevo')
        email_nuevo = request.form.get('email_nuevo')

        exito, mensaje = crear_nuevo_admin(usuario_actual['id'], usuario_nuevo, email_nuevo)
        if exito:
            exito_admin = mensaje
        else:
            error_admin = mensaje

    # Obtener lista de usuarios
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute('SELECT id, usuario, email, rol, creado_en, verified FROM usuarios ORDER BY creado_en DESC')
    usuarios = c.fetchall()
    conn.close()

    return render_template('admin.html',
                           usuarios=usuarios,
                           error_admin=error_admin,
                           exito_admin=exito_admin)

@principal.route('/admin/eliminar', methods=['POST'])
@requerir_admin
def eliminar_usuario():
    usuario_actual = obtener_usuario_actual()
    if not usuario_actual:
        return redirect(url_for('principal.login'))

    usuario_id = request.form.get('usuario_id')
    if not usuario_id:
        return redirect(url_for('principal.admin'))

    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute('SELECT id, usuario, email, rol FROM usuarios WHERE id = ?', (usuario_id,))
    usuario = c.fetchone()

    if not usuario:
        conn.close()
        return redirect(url_for('principal.admin'))

    if usuario['rol'] == 'admin':
        conn.close()
        return redirect(url_for('principal.admin'))

    email = usuario['email']
    nombre_usuario = usuario['usuario']

    try:
        c.execute('DELETE FROM usuarios WHERE id = ?', (usuario_id,))
        conn.commit()
    finally:
        conn.close()

    asunto = 'Cuenta eliminada en MigradorBD'
    mensaje = (
        f'Hola {nombre_usuario},\n\n'
        'Tu cuenta ha sido eliminada por un administrador. Si crees que esto es un error, ponte en contacto con el equipo de soporte.\n\n'
        'Saludos,\nEquipo MigradorBD'
    )
    exito_email, error_email = enviar_email_notificacion(email, asunto, mensaje)
    _registrar_log(f'Usuario eliminado por admin: {nombre_usuario}', 'warning', request.remote_addr)

    if not exito_email:
        mensaje_exito = f'Usuario {nombre_usuario} eliminado. No se pudo notificar por email: {error_email}'
    else:
        mensaje_exito = f'Usuario {nombre_usuario} eliminado y notificado por email.'

    # Recargar la lista de usuarios y mostrar mensaje de éxito
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute('SELECT id, usuario, email, rol, creado_en, verified FROM usuarios ORDER BY creado_en DESC')
    usuarios = c.fetchall()
    conn.close()

    return render_template('admin.html',
                           usuarios=usuarios,
                           exito_admin=mensaje_exito)

# ==================== RUTAS PROTEGIDAS ====================

@principal.route('/')
def index():
    if 'usuario_id' in session:
        return redirect(url_for('principal.migracion'))
    return render_template('index.html')

@principal.route('/configuracion')
@requerir_login
def configuracion():
    from flask import redirect, url_for
    return redirect(url_for('principal.migracion'))

@principal.route('/migracion')
@requerir_login
def migracion():
    usuario_actual = obtener_usuario_actual()
    return render_template('migracion.html', usuario=usuario_actual)

@principal.route('/historial')
@requerir_login
def historial():
    usuario_actual = obtener_usuario_actual()
    # Ordenar historial: más reciente primero (orden estable)
    historial_ordenado = sorted(
        estado_app['historial'],
        key=lambda x: x.get('timestamp', x.get('fecha', '')),
        reverse=True
    )
    logs_ordenados = sorted(
        estado_app['logs'],
        key=lambda x: x.get('fecha', ''),
        reverse=True
    )
    return render_template('historial.html',
                           historial=historial_ordenado,
                           logs=logs_ordenados,
                           usuario=usuario_actual)

@principal.route('/monitoreo-ip')
@requerir_admin
def monitoreo_ip():
    usuario_actual = obtener_usuario_actual()
    return render_template('monitoreo_ip.html', ips=estado_app['ips'], usuario=usuario_actual)

# Ruta de compatibilidad: redirigir /reporte a /historial
@principal.route('/reporte')
def reporte():
    from flask import redirect, url_for
    return redirect(url_for('principal.historial'))

def _esquema_serializable(esquema: dict) -> dict:
    """Convierte el esquema al formato simple de lista de columnas para la UI."""
    resultado = {}
    for tabla, info in esquema.items():
        if isinstance(info, dict):
            resultado[tabla] = info.get('columnas', [])
        else:
            resultado[tabla] = info
    return resultado


def _extension_para_motor(motor: str) -> str:
    """Devuelve una extensión de archivo recomendada según el motor destino."""
    if not motor:
        return '.db'
    m = motor.lower()
    if 'sqlite' in m:
        return '.db'
    if 'postgres' in m or 'mysql' in m or 'sql server' in m or 'oracle' in m:
        return '.sql'
    if 'mongo' in m or 'json' in m:
        return '.json'
    if 'csv' in m:
        return '.csv'
    if 'elasticsearch' in m or 'cassandra' in m:
        return '.ndjson'
    return '.db'

@principal.route('/api/subir-archivo', methods=['POST'])
@requerir_login
def api_subir_archivo():
    _registrar_actividad_ip('Subir archivo')  # Registrar actividad real
    # Validaciones básicas del archivo
    if 'archivo' not in request.files:
        return jsonify({'estado': 'error', 'mensaje': 'No se subio archivo'})

    archivo = request.files['archivo']
    if archivo.filename == '':
        return jsonify({'estado': 'error', 'mensaje': 'Archivo vacio'})

    nombre = secure_filename(archivo.filename)
    carpeta_usuario = _carpeta_upload_usuario()
    ruta = os.path.join(carpeta_usuario, nombre)

    ip = request.remote_addr or 'desconocida'
    try:
        # Guardar archivo en disco (puede lanzar excepciones en algunos entornos)
        archivo.save(ruta)
    except Exception as e:
        _registrar_log(f'Error al guardar "{nombre}": {str(e)}', 'error', ip)
        return jsonify({'estado': 'error', 'mensaje': f'No se pudo guardar el archivo: {str(e)}'})

    # Ejecutar la detección dentro de un bloque try/except para evitar 500s
    try:
        tipo, mensaje, _ = DetectorBaseDatos.detectar(ruta, nombre)
    except Exception as e:
        _registrar_log(f'Error detectando tipo para "{nombre}": {str(e)}', 'error', ip)
        return jsonify({'estado': 'error', 'mensaje': 'Error detectando tipo de archivo'})

    if tipo == 'Desconocido':
        _registrar_log(f'Archivo rechazado "{nombre}": {mensaje}', 'error', ip)
        return jsonify({'estado': 'error', 'mensaje': mensaje})

    if tipo == 'SQL Server Backup':
        _registrar_log(f'Archivo "{nombre}" identificado como backup binario: {mensaje}', 'error', ip)
        resumen_origen = _resumen_origen_detectado(tipo, mensaje)
        return jsonify({'estado': 'error', 'mensaje': mensaje, **resumen_origen})

    try:
        origen = ConectorOrigen(ruta, tipo)
        origen.mensaje_deteccion = mensaje
        objetos_detectados = (
            len(getattr(origen, 'vistas', []))
            + len(getattr(origen, 'triggers', []))
            + len(getattr(origen, 'procedimientos', []))
            + len(getattr(origen, 'funciones', []))
            + len(getattr(origen, 'indices', []))
        )

        if not origen.tablas:
            if objetos_detectados > 0:
                estado_app['origen'] = origen
                _registrar_log(
                    f'Archivo "{nombre}" sin tablas, pero con {objetos_detectados} objetos SQL detectados',
                    'warning',
                    ip,
                )
                return jsonify({
                    'estado': 'exito',
                    **_resumen_origen_detectado(tipo, mensaje),
                    'nombre_archivo': nombre,
                    'tablas': [],
                    'total_tablas': 0,
                    'esquema': {},
                    'objetos_detectados': objetos_detectados,
                    'mensaje': 'Se detectaron objetos SQL pero no tablas en el archivo.',
                    'puede_validar_tipo': True
                })

            _registrar_log(f'Archivo "{nombre}" sin tablas detectadas', 'error', ip)
            return jsonify({'estado': 'error', 'mensaje': 'No se encontraron tablas ni objetos SQL. Si el .bak es un backup binario, primero restaure y exporte a .sql.'})

        estado_app['origen'] = origen
        _registrar_log(
            f'Archivo cargado: "{nombre}" ({tipo}) - {len(origen.tablas)} tablas', 'info', ip
        )

        return jsonify({
            'estado': 'exito',
            **_resumen_origen_detectado(tipo, mensaje),
            'nombre_archivo': nombre,
            'tablas': origen.tablas,
            'total_tablas': len(origen.tablas),
            'esquema': _esquema_serializable(origen.esquema),
            'puede_validar_tipo': True
        })
    except Exception as e:
        # Registrar y devolver siempre JSON (evitar páginas HTML o trazas)
        _registrar_log(f'Error al cargar "{nombre}": {str(e)}', 'error', ip)
        return jsonify({'estado': 'error', 'mensaje': f'Error procesando archivo: {str(e)}'})


@principal.route('/api/validar-tipo-bd', methods=['POST'])
@requerir_login
def api_validar_tipo_bd():
    """Permite al usuario validar o corregir el tipo de BD detectado."""
    _registrar_actividad_ip('Validar tipo BD')
    
    datos = request.json or {}
    tipo_sugerido = (datos.get('tipo_bd') or '').strip()
    
    if not tipo_sugerido:
        return jsonify({'estado': 'error', 'mensaje': 'Debe indicar un tipo de base de datos'})
    
    # Lista de tipos válidos permitidos
    tipos_validos = [
        'SQLite', 'PostgreSQL', 'MySQL', 'MariaDB', 'Microsoft SQL Server', 'Oracle',
        'Snowflake', 'Amazon Redshift', 'Azure SQL Database', 'IBM Db2', 'Google BigQuery',
        'MongoDB', 'Elasticsearch', 'Redis', 'Apache Cassandra', 'MongoDB Atlas',
        'CSV', 'Excel', 'SQL Generico'
    ]
    
    if tipo_sugerido not in tipos_validos:
        return jsonify({
            'estado': 'error',
            'mensaje': f'Tipo "{tipo_sugerido}" no válido. Tipos permitidos: {", ".join(tipos_validos)}'
        })
    
    if not estado_app['origen']:
        return jsonify({'estado': 'error', 'mensaje': 'No hay archivo cargado'})
    
    # Cambiar el tipo de BD en el origen
    tipo_anterior = estado_app['origen'].tipo
    estado_app['origen'].tipo = tipo_sugerido
    
    ip = request.remote_addr or 'desconocida'
    _registrar_log(
        f'Tipo de BD corregido: {tipo_anterior} → {tipo_sugerido}',
        'info', ip
    )
    
    return jsonify({
        'estado': 'exito',
        'mensaje': f'Tipo de BD actualizado: {tipo_anterior} → {tipo_sugerido}',
        'tipo_anterior': tipo_anterior,
        'tipo_nuevo': tipo_sugerido,
        'tipo_detectado': tipo_sugerido,
        'motor_origen': tipo_sugerido
    })


@principal.route('/api/sugerir-tipos-bd', methods=['GET'])
def api_sugerir_tipos_bd():
    """Devuelve los tipos de BD disponibles para validación manual."""
    tipos_relacionales = [
        {'id': 'SQLite', 'nombre': 'SQLite', 'grupo': 'Relacional'},
        {'id': 'PostgreSQL', 'nombre': 'PostgreSQL', 'grupo': 'Relacional'},
        {'id': 'MySQL', 'nombre': 'MySQL', 'grupo': 'Relacional'},
        {'id': 'MariaDB', 'nombre': 'MariaDB', 'grupo': 'Relacional'},
        {'id': 'Microsoft SQL Server', 'nombre': 'Microsoft SQL Server', 'grupo': 'Relacional'},
        {'id': 'Oracle', 'nombre': 'Oracle', 'grupo': 'Relacional'},
        {'id': 'Snowflake', 'nombre': 'Snowflake', 'grupo': 'Relacional'},
        {'id': 'Amazon Redshift', 'nombre': 'Amazon Redshift', 'grupo': 'Relacional'},
        {'id': 'Azure SQL Database', 'nombre': 'Azure SQL Database', 'grupo': 'Relacional'},
        {'id': 'IBM Db2', 'nombre': 'IBM Db2', 'grupo': 'Relacional'},
        {'id': 'Google BigQuery', 'nombre': 'Google BigQuery', 'grupo': 'Relacional'},
    ]
    
    tipos_no_relacionales = [
        {'id': 'MongoDB', 'nombre': 'MongoDB', 'grupo': 'No Relacional'},
        {'id': 'MongoDB Atlas', 'nombre': 'MongoDB Atlas', 'grupo': 'No Relacional'},
        {'id': 'Elasticsearch', 'nombre': 'Elasticsearch', 'grupo': 'No Relacional'},
        {'id': 'Redis', 'nombre': 'Redis', 'grupo': 'No Relacional'},
        {'id': 'Apache Cassandra', 'nombre': 'Apache Cassandra', 'grupo': 'No Relacional'},
    ]
    
    tipos_otros = [
        {'id': 'CSV', 'nombre': 'CSV', 'grupo': 'Otros'},
        {'id': 'Excel', 'nombre': 'Excel', 'grupo': 'Otros'},
        {'id': 'SQL Generico', 'nombre': 'SQL Genérico', 'grupo': 'Otros'},
    ]
    
    return jsonify({
        'tipos': tipos_relacionales + tipos_no_relacionales + tipos_otros,
        'grupos': {
            'Relacional': tipos_relacionales,
            'No Relacional': tipos_no_relacionales,
            'Otros': tipos_otros
        }
    })


@principal.route('/api/subir-a-github', methods=['POST'])
@requerir_login
def api_subir_a_github():
    """Endpoint para subir un archivo ya presente en `uploads/` a un repo de GitHub.

    JSON esperado: {
      'repo': 'owner/repo',
      'path': 'ruta/en/repo/archivo.ext',
      'archivo': 'nombre_local_en_uploads',
      'mensaje': 'Mensaje del commit'
    }
    """
    _registrar_actividad_ip('Subir a GitHub')
    datos = request.json or {}
    repo = datos.get('repo')
    path = datos.get('path')
    archivo = datos.get('archivo')
    mensaje = datos.get('mensaje') or f'Subida desde MigradorBD: {archivo}'

    if not repo or not path or not archivo:
        return jsonify({'estado': 'error', 'mensaje': 'Faltan campos: repo, path o archivo'})

    local_path = os.path.join(_carpeta_upload_usuario(), secure_filename(archivo))
    if not os.path.exists(local_path):
        return jsonify({'estado': 'error', 'mensaje': f'Archivo no encontrado: {archivo}'})

    from app.github_integration import upload_file_to_github

    resultado = upload_file_to_github(repo, path, local_path, mensaje)
    if resultado.get('exito'):
        _registrar_log(f'Archivo {archivo} subido a GitHub: {repo}/{path}', 'info', request.remote_addr)
        return jsonify({'estado': 'exito', 'mensaje': resultado.get('mensaje'), 'url': resultado.get('url')})
    else:
        _registrar_log(f'Error subiendo {archivo} a GitHub: {resultado.get("mensaje")}', 'error', request.remote_addr)
        return jsonify({'estado': 'error', 'mensaje': resultado.get('mensaje')})

@principal.route('/api/configurar-destino', methods=['POST'])
@requerir_login
def api_configurar_destino():
    _registrar_actividad_ip('Configurar destino')  # Registrar actividad real
    datos = request.json
    motor = datos.get('motor_destino', 'SQLite')
    ip = request.remote_addr or 'desconocida'
    
    try:
        destino = CargadorDestino(motor)
        estado_app['destino'] = destino
        
        if estado_app['origen'] and estado_app['origen'].esquema:
            creadas = destino.crear_estructura(estado_app['origen'].esquema)
            _registrar_log(
                f'Destino {motor} configurado: {creadas} tablas/estructuras creadas', 'info', ip
            )
            # Pasar información de esquemas al destino
            if hasattr(estado_app['origen'], 'tabla_a_esquema'):
                destino.tabla_a_esquema = estado_app['origen'].tabla_a_esquema
        
            if estado_app['origen']:
                # Crear esquemas primero (si es soportado)
                if hasattr(estado_app['origen'], 'esquemas'):
                    esquemas_creados = destino.crear_esquemas(estado_app['origen'].esquemas)
                    _registrar_log(f'Esquemas creados: {esquemas_creados}', 'info', ip)
            
                # Luego crear tablas con sus esquemas
                if estado_app['origen'].esquema:
                    creadas = destino.crear_estructura(
                        estado_app['origen'].esquema,
                        tabla_a_esquema=destino.tabla_a_esquema
                    )
                    _registrar_log(
                        f'Destino {motor} configurado: {creadas} tablas/estructuras creadas', 'info', ip
                    )
        
        return jsonify({
            'estado': 'exito',
            'mensaje': f'Destino {motor} configurado. Archivo: {os.path.basename(destino.ruta_salida)}',
            'motor': motor
        })
    except Exception as e:
        _registrar_log(f'Error configurando destino {motor}: {str(e)}', 'error', ip)
        return jsonify({'estado': 'error', 'mensaje': str(e)})

@principal.route('/api/iniciar-migracion', methods=['POST'])
@requerir_login
def api_iniciar_migracion():
    _registrar_actividad_ip('Iniciar migración')  # Registrar actividad real
    if not estado_app['origen']:
        return jsonify({'estado': 'error', 'mensaje': 'Suba un archivo primero'})
    if not estado_app['destino']:
        return jsonify({'estado': 'error', 'mensaje': 'Configure el destino primero'})
    if estado_app['proceso_activo']:
        return jsonify({'estado': 'error', 'mensaje': 'Ya hay una migracion en curso'})
    
    ip = request.remote_addr or 'desconocida'
    estado_app['proceso_activo'] = True
    estado_app['metricas'] = {'extraidos': 0, 'cargados': 0, 'errores': 0, 'tablas_ok': 0}
    estado_app['_ip_migracion'] = ip  # Guardar IP para el background task
    
    _registrar_log('Iniciando migracion...', 'info', ip)
    
    socketio.start_background_task(ejecutar_migracion)
    return jsonify({'estado': 'exito'})

def ejecutar_migracion():
    origen = estado_app.get('origen')
    destino = estado_app.get('destino')
    tablas = origen.tablas if origen else []
    total = len(tablas)
    
    # Guardar timestamp de inicio para calcular duración
    estado_app['_fecha_inicio_migracion'] = datetime.now()

    _registrar_log(f'Migrando {total} tablas...')

    if total == 0:
        try:
            estado_app['proceso_activo'] = False
            _registrar_log('No hay tablas para migrar', 'warning')
            socketio.emit('progreso', {
                'porcentaje': 100,
                'tabla': '',
                'estado': 'No hay tablas para migrar',
                'metricas': estado_app['metricas']
            }, skip_sid=None)
            socketio.emit('migracion_completada', estado_app['metricas'], skip_sid=None)
        finally:
            return

    try:
        for idx, tabla in enumerate(tablas):
            if not estado_app['proceso_activo']:
                _registrar_log('Migracion pausada por el usuario', 'warning')
                break

            progreso = int(((idx + 1) / total) * 100) if total > 0 else 100

            try:
                _registrar_log(f'Extrayendo: {tabla}...')
                df = origen.extraer_datos(tabla)
                estado_app['metricas']['extraidos'] += len(df)

                if not df.empty:
                    _registrar_log(f'Cargando: {tabla} ({len(df)} registros)...')
                    df = MapeadorDatos.limpiar_dataframe(df)
                    cargados = destino.cargar_tabla(tabla, df)
                    estado_app['metricas']['cargados'] += cargados

                estado_app['metricas']['tablas_ok'] += 1

                socketio.emit('progreso', {
                    'porcentaje': progreso,
                    'tabla': tabla,
                    'estado': f'{tabla}: {len(df)} registros migrados',
                    'metricas': estado_app['metricas']
                }, skip_sid=None)

            except Exception as e:
                estado_app['metricas']['errores'] += 1
                _registrar_log(f'ERROR en {tabla}: {str(e)}', 'error')
                socketio.emit('progreso', {
                    'porcentaje': int(((idx + 1) / total) * 100) if total > 0 else 0,
                    'tabla': tabla,
                    'estado': f'ERROR en {tabla}: {str(e)}',
                    'metricas': estado_app['metricas']
                }, skip_sid=None)
    finally:
        # Asegurar que siempre se marca como terminado y se notifica al cliente
        try:
            estado_app['proceso_activo'] = False

            # Crear vistas, triggers, procedimientos y funciones
            if origen and destino:
                _registrar_log('Creando objetos de BD (vistas, triggers, procedimientos)...')
                
                # Crear vistas
                if hasattr(origen, 'vistas') and origen.vistas:
                    vistas_creadas = destino.crear_vistas(origen.vistas)
                    _registrar_log(f'Vistas creadas: {vistas_creadas}')
                
                # Crear triggers
                if hasattr(origen, 'triggers') and origen.triggers:
                    triggers_creados = destino.crear_triggers(origen.triggers)
                    _registrar_log(f'Triggers creados: {triggers_creados}')

                # Crear indices
                if hasattr(origen, 'indices') and origen.indices:
                    indices_creados = destino.crear_indices(origen.indices)
                    _registrar_log(f'Indices registrados: {indices_creados}')
                
                # Crear procedimientos
                if hasattr(origen, 'procedimientos') and origen.procedimientos:
                    procs_creados = destino.crear_procedimientos(origen.procedimientos)
                    _registrar_log(f'Procedimientos procesados: {procs_creados}')
                
                # Crear funciones
                if hasattr(origen, 'funciones') and origen.funciones:
                    funcs_creadas = destino.crear_funciones(origen.funciones)
                    _registrar_log(f'Funciones procesadas: {funcs_creadas}')

            if origen:
                # Registrar en historial con más detalles
                ahora = datetime.now()
                estado_app['historial'].append({
                    'id': len(estado_app['historial']) + 1,
                    'fecha': ahora.isoformat(),
                    'timestamp': ahora.strftime('%Y-%m-%d %H:%M:%S'),
                    'metricas': estado_app['metricas'].copy(),
                    'motor_destino': destino.motor if destino else None,
                    'archivo_origen': os.path.basename(origen.ruta) if getattr(origen, 'ruta', None) else '',
                    'total_tablas': total,
                    'ip': estado_app.get('_ip_migracion', 'desconocida'),
                    'usuario': 'sistema',
                    'duracion_segundos': (ahora - (estado_app.get('_fecha_inicio_migracion', ahora))).total_seconds()
                })

            _registrar_log(
                f'Migracion finalizada. Tablas: {estado_app["metricas"].get("tablas_ok",0)}, '
                f'Registros: {estado_app["metricas"].get("cargados",0)}, '
                f'Errores: {estado_app["metricas"].get("errores",0)}'
            )

            socketio.emit('progreso', {
                'porcentaje': 100,
                'tabla': '',
                'estado': 'Migracion completada',
                'metricas': estado_app['metricas']
            }, skip_sid=None)

            socketio.emit('migracion_completada', estado_app['metricas'], skip_sid=None)
            socketio.emit('limpiar_interfaz', {}, skip_sid=None)
        except Exception as e:
            _registrar_log(f'Error al finalizar migracion: {str(e)}', 'error')

@principal.route('/api/descargar')
@requerir_login
def api_descargar():
    """Descarga adaptable según motor destino con formato específico de cada BD"""
    _registrar_actividad_ip('Descargar migración')  # Registrar actividad real
    if not estado_app['destino']:
        return jsonify({'estado': 'error', 'mensaje': 'No hay migración. Ejecute una migracion primero.'})
    
    destino = estado_app['destino']
    # Permite forzar formato con query param ?motor=..., por defecto usa el motor configurado
    motor = request.args.get('motor') or (destino.motor if destino else None)
    
    try:
        # Generar exportación en formato específico del motor solicitado
        resultado, ext, mimetype, es_binario = destino.generar_export(motor)
        
        if not resultado:
            return jsonify({'estado': 'error', 'mensaje': 'Error generando exportación'})
        
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        
        # Si es binario (SQLite), usar directamente el archivo
        if es_binario:
            nombre_archivo = f'migracion_{timestamp}{ext}'
            if os.path.exists(resultado):
                try:
                    return send_file(resultado, as_attachment=True, download_name=nombre_archivo, mimetype=mimetype)
                except TypeError:
                    return send_file(resultado, as_attachment=True, attachment_filename=nombre_archivo, mimetype=mimetype)
        
        # Si es texto, escribir en archivo temporal
        else:
            nombre_archivo = f'migracion_{timestamp}{ext}'
            ruta_temp = os.path.join(UPLOAD_FOLDER, nombre_archivo)
            
            with open(ruta_temp, 'w', encoding='utf-8') as f:
                f.write(resultado)
            
            # Para JSON, Cassandra CQL y Redis, usar application/octet-stream para forzar descarga
            # en lugar de mostrar en navegador
            if ext in ['.json', '.cql', '.redis', '.ndjson']:
                mimetype = 'application/octet-stream'
            
            try:
                return send_file(ruta_temp, as_attachment=True, download_name=nombre_archivo, mimetype=mimetype)
            except TypeError:
                return send_file(ruta_temp, as_attachment=True, attachment_filename=nombre_archivo, mimetype=mimetype)
    
    except Exception as e:
        _registrar_log(f'Error generando exportación: {str(e)}', 'error')
        return jsonify({'estado': 'error', 'mensaje': f'Error: {str(e)}'})


@principal.route('/api/descargar-todo')
@requerir_login
def api_descargar_todo():
    """Crea un ZIP con la base de datos resultante y un reporte JSON, y lo devuelve."""
    _registrar_actividad_ip('Descargar paquete completo')  # Registrar actividad real
    if estado_app['destino']:
        destino = estado_app['destino']
        ruta = destino.get_ruta_salida()
        if ruta and os.path.exists(ruta):
            timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
            motor = destino.motor if destino else 'unknown'
            motor_safe = motor.lower().replace(' ', '_')
            nombre_zip = f'migracion_paquete_{motor_safe}_{timestamp}.zip'
            ruta_zip = os.path.join(UPLOAD_FOLDER, nombre_zip)

            # Construir archivo de reporte temporal
            reporte = {
                'metricas': estado_app.get('metricas', {}),
                'historial': estado_app.get('historial', [])[-10:],
                'logs_recientes': estado_app.get('logs', [])[-200:]
            }

            reporte_path = os.path.join(UPLOAD_FOLDER, f'reporte_migracion_{timestamp}.json')
            try:
                with open(reporte_path, 'w', encoding='utf-8') as f:
                    json.dump(reporte, f, ensure_ascii=False, indent=2)

                # Crear ZIP
                ext = _extension_para_motor(destino.motor if destino else None)
                arc_db_name = f'migracion_resultado{ext}'
                with zipfile.ZipFile(ruta_zip, 'w', zipfile.ZIP_DEFLATED) as zf:
                    # incluir la DB con nombre que refleje el destino
                    zf.write(ruta, arcname=arc_db_name)
                    zf.write(reporte_path, arcname=os.path.basename(reporte_path))

                nombre = os.path.basename(ruta_zip)
                try:
                    return send_file(ruta_zip, as_attachment=True, download_name=nombre)
                except TypeError:
                    return send_file(ruta_zip, as_attachment=True, attachment_filename=nombre)
            finally:
                # Intentar eliminar el archivo de reporte temporal (el ZIP puede quedarse para auditoría)
                try:
                    if os.path.exists(reporte_path):
                        os.remove(reporte_path)
                except Exception:
                    pass

    return jsonify({'estado': 'error', 'mensaje': 'No hay archivo para descargar. Ejecute una migracion primero.'})

@principal.route('/api/descargar-sql')
@requerir_login
def api_descargar_sql():
    """Descarga el SQL dump de la migración realizada"""
    _registrar_actividad_ip('Descargar SQL dump')  # Registrar actividad real
    if estado_app['destino']:
        destino = estado_app['destino']
        try:
            sql_dump = destino.generar_sql_dump()
            if sql_dump:
                timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
                nombre_archivo = f'migracion_dump_{timestamp}.sql'
                
                # Crear archivo temporal
                ruta_temp = os.path.join(UPLOAD_FOLDER, nombre_archivo)
                with open(ruta_temp, 'w', encoding='utf-8') as f:
                    f.write(sql_dump)
                
                try:
                    return send_file(ruta_temp, as_attachment=True, download_name=nombre_archivo, mimetype='application/sql')
                except TypeError:
                    return send_file(ruta_temp, as_attachment=True, attachment_filename=nombre_archivo, mimetype='application/sql')
        except Exception as e:
            _registrar_log(f'Error generando SQL dump: {str(e)}', 'error')
            return jsonify({'estado': 'error', 'mensaje': f'Error: {str(e)}'})
    
    return jsonify({'estado': 'error', 'mensaje': 'No hay migración completada. Ejecute una migracion primero.'})

@principal.route('/api/pausar', methods=['POST'])
@requerir_login
def api_pausar():
    _registrar_actividad_ip('Pausar migración')  # Registrar actividad real
    estado_app['proceso_activo'] = False
    ip = request.remote_addr or 'desconocida'
    _registrar_log('Migracion pausada', 'warning', ip)
    return jsonify({'estado': 'exito'})


@principal.route('/api/crear-estructura', methods=['POST'])
@requerir_login
def api_crear_estructura():
    """Endpoint para crear la estructura en el destino desde la UI."""
    _registrar_actividad_ip('Crear estructura')  # Registrar actividad real
    ip = request.remote_addr or 'desconocida'
    if not estado_app.get('destino'):
        _registrar_log('Intento de crear estructura sin destino configurado', 'error', ip)
        return jsonify({'estado': 'error', 'mensaje': 'Configure el destino primero'})

    destino = estado_app['destino']
    try:
        if estado_app.get('origen') and estado_app['origen'].esquema:
            creadas = destino.crear_estructura(estado_app['origen'].esquema)
            _registrar_log(f'Estructura creada: {creadas} tablas', 'info', ip)
            return jsonify({'estado': 'exito', 'mensaje': f'Estructura creada: {creadas} tablas'})
        else:
            _registrar_log('No hay esquema de origen para crear estructura', 'error', ip)
            return jsonify({'estado': 'error', 'mensaje': 'No hay esquema de origen. Suba un archivo primero.'})
    except Exception as e:
        _registrar_log(f'Error creando estructura: {str(e)}', 'error', ip)
        return jsonify({'estado': 'error', 'mensaje': str(e)})

@principal.route('/api/estado')
def api_estado():
    if estado_app['origen']:
        origen = estado_app['origen']
        return jsonify({
            'estado': 'exito',
            'tipo_detectado': origen.tipo,
            'motor_origen': origen.tipo,
            'mensaje_deteccion': getattr(origen, 'mensaje_deteccion', ''),
            'tablas': origen.tablas,
            'total_tablas': len(origen.tablas),
            'esquema': _esquema_serializable(origen.esquema),
            'motor_destino': estado_app['destino'].motor if estado_app['destino'] else None,
            'metricas': estado_app['metricas'],
            'proceso_activo': estado_app['proceso_activo']
        })
    return jsonify({'estado': 'sin_origen'})

@principal.route('/api/historial')
def api_historial():
    # Devolver historial ordenado: más reciente primero
    historial_ordenado = sorted(
        estado_app['historial'],
        key=lambda x: x.get('timestamp', x.get('fecha', '')),
        reverse=True
    )
    resp = jsonify({'historial': historial_ordenado, 'logs': estado_app['logs']})
    # Sin caché para datos en tiempo real
    resp.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    resp.headers['Pragma'] = 'no-cache'
    resp.headers['Expires'] = '0'
    return resp

@principal.route('/api/ips')
def api_ips():
    return jsonify({'ips': estado_app['ips']})

@socketio.on('conectar')
def conectar():
    socketio.emit('log', {'mensaje': 'Sistema listo. Suba un archivo para comenzar.'})