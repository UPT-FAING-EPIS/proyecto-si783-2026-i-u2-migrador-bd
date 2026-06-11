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
    registrar_usuario_oauth, verificar_codigo, enviar_email_notificacion,
    obtener_perfil_usuario, actualizar_perfil_usuario
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

from flask import session, has_request_context
from threading import local

thread_local = local()

class EstadoProxy:
    _global_ips = []
    _global_logs = []

    def __init__(self):
        self._estados = {}

    def _get_current_uid(self):
        if hasattr(thread_local, 'usuario_id') and thread_local.usuario_id:
            return thread_local.usuario_id
        try:
            if has_request_context():
                return session.get('usuario_id', 'anonimo')
        except Exception:
            pass
        return 'anonimo'

    def get_estado(self):
        uid = self._get_current_uid()
        if uid not in self._estados:
            self._estados[uid] = {
                'origen': None,
                'destino': None,
                'proceso_activo': False,
                'metricas': {'extraidos': 0, 'cargados': 0, 'errores': 0, 'tablas_ok': 0},
                'historial': [],
            }
        return self._estados[uid]

    def __getitem__(self, key):
        if key == 'ips':
            return self._global_ips
        if key == 'logs':
            return self._global_logs
        return self.get_estado()[key]

    def __setitem__(self, key, value):
        if key == 'ips':
            self._global_ips = value
        elif key == 'logs':
            self._global_logs = value
        else:
            self.get_estado()[key] = value

    def __contains__(self, key):
        if key in ['ips', 'logs']:
            return True
        return key in self.get_estado()

    def get(self, key, default=None):
        if key == 'ips':
            return self._global_ips
        if key == 'logs':
            return self._global_logs
        return self.get_estado().get(key, default)

estado_app = EstadoProxy()

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
    from app.local_state import registrar_ip_compartida
    registrar_ip_compartida(ip, actividad, usuario)

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
            perfil = obtener_perfil_usuario(usuario_data['id'])
            if perfil and perfil.get('foto_perfil'):
                session['tiene_foto'] = True
            else:
                session['tiene_foto'] = False
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

@principal.route('/api/github/desconectar', methods=['POST'])
@requerir_login
def api_github_desconectar():
    """Desconecta la cuenta de GitHub."""
    session.pop('github_access_token', None)
    session.pop('github_token_type', None)
    return jsonify({'estado': 'exito'})

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
                    from app.auth import obtener_perfil_usuario
                    perfil = obtener_perfil_usuario(usuario_data['id'])
                    if perfil and perfil.get('foto_perfil'):
                        session['tiene_foto'] = True
                    else:
                        session['tiene_foto'] = False
                    _registrar_log(
                        f'Usuario {usuario_data["usuario"]} inició sesión con Google',
                        'info', request.remote_addr
                    )
                    return redirect(url_for('principal.migracion'))

        elif proveedor.lower() == 'github':
            token = oauth.github.authorize_access_token()
            session['github_access_token'] = token.get('access_token')
            session['github_token_type'] = token.get('token_type', 'bearer')

            if action == 'connect':
                return "<script>window.close();</script>"

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
                    from app.auth import obtener_perfil_usuario
                    perfil = obtener_perfil_usuario(usuario_data['id'])
                    if perfil and perfil.get('foto_perfil'):
                        session['tiene_foto'] = True
                    else:
                        session['tiene_foto'] = False
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


@principal.route('/api/github/ramas', methods=['GET'])
@requerir_login
def api_github_ramas():
    """Obtiene las ramas de un repositorio de GitHub."""
    headers = _github_headers()
    if not headers:
        return jsonify({'estado': 'error', 'mensaje': 'Conecta tu cuenta de GitHub primero'}), 401

    repo = request.args.get('repo')
    if not repo:
        return jsonify({'estado': 'error', 'mensaje': 'Falta el repositorio'}), 400

    try:
        url = f'https://api.github.com/repos/{repo}/branches?per_page=100'
        respuesta = requests.get(url, headers=headers, timeout=20)
        if respuesta.status_code != 200:
            return jsonify({'estado': 'error', 'mensaje': f'GitHub respondió {respuesta.status_code}'}), 400

        ramas = [{'name': b.get('name')} for b in respuesta.json()]
        return jsonify({'estado': 'exito', 'ramas': ramas})
    except Exception as e:
        return jsonify({'estado': 'error', 'mensaje': str(e)}), 500


@principal.route('/api/github/commits', methods=['GET'])
@requerir_login
def api_github_commits():
    """Obtiene los últimos commits de una rama en GitHub."""
    headers = _github_headers()
    if not headers:
        return jsonify({'estado': 'error', 'mensaje': 'Conecta tu cuenta de GitHub primero'}), 401

    repo = request.args.get('repo')
    branch = request.args.get('branch', 'main')
    if not repo:
        return jsonify({'estado': 'error', 'mensaje': 'Falta el repositorio'}), 400

    try:
        url = f'https://api.github.com/repos/{repo}/commits?sha={branch}&per_page=5'
        respuesta = requests.get(url, headers=headers, timeout=20)
        if respuesta.status_code != 200:
            return jsonify({'estado': 'error', 'mensaje': f'GitHub respondió {respuesta.status_code}'}), 400

        commits = []
        for c in respuesta.json():
            commits.append({
                'sha': c.get('sha')[:7] if c.get('sha') else '',
                'mensaje': c.get('commit', {}).get('message', ''),
                'fecha': c.get('commit', {}).get('author', {}).get('date', ''),
                'url': c.get('html_url', '')
            })
        return jsonify({'estado': 'exito', 'commits': commits})
    except Exception as e:
        return jsonify({'estado': 'error', 'mensaje': str(e)}), 500


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


@principal.route('/api/github/archivos-migrados', methods=['GET'])
@requerir_login
def api_github_archivos_migrados():
    """Retorna un archivo virtual si hay una migración en memoria."""
    try:
        archivos = []
        if estado_app.get('destino'):
            motor = estado_app['destino'].motor
            ext = _extension_para_motor(motor)
            timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
            nombre = f'migracion_{motor.replace(" ", "_")}_{timestamp}{ext}'
            archivos.append({'nombre': nombre})
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

    es_migrado = datos.get('es_migrado', False)

    try:
        if es_migrado and estado_app.get('destino'):
            # Generar archivo en el momento de subir
            resultado, ext, mimetype, es_binario = estado_app['destino'].generar_export(None)
            if not resultado:
                return jsonify({'estado': 'error', 'mensaje': 'No se pudo generar la exportación'}), 500
                
            if es_binario:
                with open(resultado, 'rb') as f:
                    contenido = f.read()
            else:
                contenido = resultado.encode('utf-8')
        else:
            local_path = os.path.join(_carpeta_upload_usuario(), secure_filename(archivo))
            if not os.path.exists(local_path):
                return jsonify({'estado': 'error', 'mensaje': f'Archivo no encontrado: {archivo}'}), 404
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
    from app.local_state import obtener_ips_compartidas
    ips_globales = obtener_ips_compartidas()
    return render_template('monitoreo_ip.html', ips=ips_globales, usuario=usuario_actual)


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

@principal.route('/api/cli/execute', methods=['POST'])
@requerir_login
def api_cli_execute():
    datos = request.json or {}
    comando_str = datos.get('command', '').strip()
    if not comando_str:
        return jsonify({'html': ''})
    
    args = comando_str.split()
    cmd = args[0].lower()
    
    _registrar_actividad_ip(f'CLI: {comando_str}')
    
    # Reconstruir estado desde sesión si estamos en un worker distinto
    if not estado_app.get('origen'):
        archivo_actual = session.get('archivo_actual')
        tipo_origen = session.get('tipo_origen')
        if archivo_actual and tipo_origen:
            try:
                ruta = os.path.join(_carpeta_upload_usuario(), archivo_actual)
                if os.path.exists(ruta):
                    origen = ConectorOrigen(ruta, tipo_origen)
                    if origen.tablas:
                        estado_app['origen'] = origen
            except Exception:
                pass
                
    if not estado_app.get('destino'):
        motor_destino = session.get('motor_destino')
        if motor_destino:
            try:
                estado_app['destino'] = CargadorDestino(motor_destino)
            except Exception:
                pass
    
    if cmd == 'help':
        html = """
        <div style="color: #60a5fa; font-weight: bold; margin-bottom: 5px;">Comandos Disponibles:</div>
        <div style="display: grid; grid-template-columns: 220px 1fr; gap: 5px; margin-bottom: 10px;">
            <span class="color-yellow">help</span><span class="color-gray">Muestra este mensaje de ayuda.</span>
            <span class="color-yellow">ls uploads</span><span class="color-gray">Lista los archivos disponibles en tu carpeta local.</span>
            <span class="color-yellow">load origin &lt;archivo&gt;</span><span class="color-gray">Carga un archivo de origen en memoria.</span>
            <span class="color-yellow">connect dest &lt;motor&gt;</span><span class="color-gray">Conecta el destino (ej. mysql, postgres).</span>
            <span class="color-yellow">status</span><span class="color-gray">Muestra el estado actual de las conexiones y tablas.</span>
            <span class="color-yellow">migrate</span><span class="color-gray">Inicia la migración de datos al destino de forma asíncrona.</span>
            <span class="color-yellow">clear</span><span class="color-gray">Limpia la terminal.</span>
        </div>
        """
        return jsonify({'html': html})

    elif cmd == 'ls':
        if len(args) > 1 and args[1].lower() == 'uploads':
            carpeta_usuario = _carpeta_upload_usuario()
            archivos = os.listdir(carpeta_usuario)
            if not archivos:
                return jsonify({'html': '<span class="color-gray">No hay archivos en la carpeta uploads.</span>'})
            html = '<div style="display: flex; flex-wrap: wrap; gap: 15px;">'
            for f in archivos:
                color = "color-blue" if f.endswith('.sql') or f.endswith('.bak') else "color-gray"
                html += f'<span class="{color}">{f}</span>'
            html += '</div>'
            return jsonify({'html': html})
        else:
            return jsonify({'html': '<span class="color-red">Comando ls requiere un argumento (ej: ls uploads).</span>'})

    elif cmd == 'load' and len(args) > 1 and args[1].lower() == 'origin':
        if len(args) < 3:
            return jsonify({'html': '<span class="color-red">Debes especificar el nombre del archivo.</span>'})
        archivo = args[2]
        ruta = os.path.join(_carpeta_upload_usuario(), secure_filename(archivo))
        if not os.path.exists(ruta):
            return jsonify({'html': f'<span class="color-red">Archivo no encontrado: {archivo}</span>'})
        
        tipo, msg, _ = DetectorBaseDatos.detectar(ruta, archivo)
        if tipo == 'Desconocido' or tipo == 'SQL Server Backup':
            return jsonify({'html': f'<span class="color-red">No se pudo cargar: {msg}</span>'})
        
        try:
            origen = ConectorOrigen(ruta, tipo)
            if not origen.tablas:
                return jsonify({'html': '<span class="color-red">El archivo no contiene tablas.</span>'})
            estado_app['origen'] = origen
            session['archivo_actual'] = archivo
            session['tipo_origen'] = tipo
            html = f'<span class="color-green">Origen cargado exitosamente: {len(origen.tablas)} tablas detectadas ({tipo}).</span>'
            return jsonify({'html': html})
        except Exception as e:
            return jsonify({'html': f'<span class="color-red">Error cargando origen: {str(e)}</span>'})

    elif cmd == 'connect' and len(args) > 1 and args[1].lower() == 'dest':
        if len(args) < 3:
            return jsonify({'html': '<span class="color-red">Debes especificar el motor (ej: MySQL, PostgreSQL, MongoDB, Cassandra).</span>'})
        motor = " ".join(args[2:]).strip()
        
        motores_validos = ["MySQL", "PostgreSQL", "SQL Server", "Oracle", "MongoDB", "Cassandra", "Elasticsearch", "Redis", "SQLite"]
        motor_formateado = next((m for m in motores_validos if m.lower() == motor.lower()), None)
        
        if not motor_formateado:
            return jsonify({'html': f'<span class="color-red">Motor no soportado. Usa uno de: {", ".join(motores_validos)}</span>'})
        
        try:
            estado_app['destino'] = CargadorDestino(motor=motor_formateado)
            session['motor_destino'] = motor_formateado
            return jsonify({'html': f'<span class="color-green">Destino conectado exitosamente en modo: {motor_formateado}.</span>'})
        except Exception as e:
            return jsonify({'html': f'<span class="color-red">Error conectando destino: {str(e)}</span>'})

    elif cmd == 'status':
        origen = estado_app.get('origen')
        destino = estado_app.get('destino')
        
        html = '<div style="margin-bottom: 10px;">'
        if origen:
            html += f'<div style="margin-bottom: 5px;"><span class="color-blue font-bold">Origen:</span> <span class="color-green">Cargado ({len(origen.tablas)} tablas, {origen.motor})</span></div>'
        else:
            html += '<div style="margin-bottom: 5px;"><span class="color-blue font-bold">Origen:</span> <span class="color-red">No cargado</span></div>'
            
        if destino:
            html += f'<div><span class="color-blue font-bold">Destino:</span> <span class="color-green">Conectado ({destino.motor})</span></div>'
        else:
            html += '<div><span class="color-blue font-bold">Destino:</span> <span class="color-red">No conectado</span></div>'
        html += '</div>'
        
        if origen:
            html += '<div style="color: #60a5fa; font-weight: bold; margin-bottom: 5px;">Tablas en Origen:</div>'
            html += '<table style="width: 100%; max-width: 500px; border-collapse: collapse; font-size: 13px; margin-bottom: 10px; border: 1px solid #334155;">'
            html += '<tr style="border-bottom: 1px solid #334155; background: #1e293b; color: #94a3b8;"><th style="text-align: left; padding: 6px;">Tabla</th><th style="text-align: left; padding: 6px;">Registros</th></tr>'
            for t in origen.tablas[:10]:
                html += f'<tr style="border-bottom: 1px solid #1e293b;"><td style="padding: 6px; border-right: 1px solid #334155;">{t["nombre"]}</td><td style="padding: 6px;">{t["registros"]}</td></tr>'
            if len(origen.tablas) > 10:
                html += f'<tr><td colspan="2" style="padding: 6px; color: #94a3b8; text-align:center;">...y {len(origen.tablas) - 10} más</td></tr>'
            html += '</table>'
            
        return jsonify({'html': html})

    elif cmd == 'migrate':
        if not estado_app.get('origen') or not estado_app.get('destino'):
            return jsonify({'html': '<span class="color-red">Debe conectar un origen y un destino primero. Use `load origin` y `connect dest`.</span>'})
        if estado_app.get('proceso_activo'):
            return jsonify({'html': '<span class="color-yellow">Ya hay una migración en progreso.</span>'})
        
        estado_app['proceso_activo'] = True
        estado_app['simulacion'] = False
        estado_app['metricas'] = {'extraidos': 0, 'cargados': 0, 'errores': 0, 'tablas_ok': 0}
        estado_app['_ip_migracion'] = request.remote_addr or 'desconocida'
        usuario_id = session.get('usuario_id', 'anonimo')
        estado_app['_usuario_id'] = usuario_id
        
        socketio.start_background_task(ejecutar_migracion, usuario_id)
        
        html = """
        <div class="color-green" style="margin-bottom: 5px;">[✓] Migración iniciada en segundo plano.</div>
        <div class="color-gray">El progreso se mostrará automáticamente en la consola de Migración de la interfaz gráfica. Puedes revisar las métricas en tiempo real.</div>
        """
        return jsonify({'html': html})

    else:
        return jsonify({'html': f'<span class="color-red">Comando no reconocido: {cmd}. Escribe "help" para ver los comandos.</span>'})


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

    # Ejecutar la detección con reintentos para evitar bloqueos por antivirus en Windows
    try:
        import time
        intentos = 0
        tipo = 'Desconocido'
        mensaje = 'Error detectando tipo'
        _dummy = None
        while intentos < 3:
            try:
                tipo, mensaje, _dummy = DetectorBaseDatos.detectar(ruta, nombre)
                if tipo != 'Desconocido':
                    break
            except Exception:
                pass
            time.sleep(0.5)
            intentos += 1
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
        session['archivo_actual'] = nombre
        session['tipo_origen'] = tipo
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

@principal.route('/api/comparar-esquemas', methods=['POST'])
@requerir_login
def api_comparar_esquemas():
    _registrar_actividad_ip('Comparar esquemas')
    if 'origen' not in estado_app:
        return jsonify({'estado': 'error', 'mensaje': 'Primero debe subir el archivo origen.'})
        
    if 'archivo' not in request.files:
        return jsonify({'estado': 'error', 'mensaje': 'No se subio archivo de destino'})

    archivo = request.files['archivo']
    if archivo.filename == '':
        return jsonify({'estado': 'error', 'mensaje': 'Archivo vacio'})

    nombre = secure_filename(archivo.filename)
    carpeta_usuario = _carpeta_upload_usuario()
    ruta = os.path.join(carpeta_usuario, nombre)
    ip = request.remote_addr or 'desconocida'

    try:
        archivo.save(ruta)
    except Exception as e:
        return jsonify({'estado': 'error', 'mensaje': f'No se pudo guardar: {str(e)}'})

    try:
        tipo, mensaje, _ = DetectorBaseDatos.detectar(ruta, nombre)
        if tipo == 'Desconocido':
            return jsonify({'estado': 'error', 'mensaje': f'Archivo destino no válido: {mensaje}'})
            
        destino = ConectorOrigen(ruta, tipo)
        
        # Comparar estado_app['origen'].esquema vs destino.esquema
        origen = estado_app['origen']
        tablas_origen = set(origen.esquema.keys())
        tablas_destino = set(destino.esquema.keys())
        
        nuevas = list(tablas_origen - tablas_destino)
        faltantes = list(tablas_destino - tablas_origen)
        comunes = list(tablas_origen & tablas_destino)
        
        columnas_modificadas = []
        for t in comunes:
            cols_origen = {c['nombre'].lower(): c for c in origen.esquema[t].get('columnas', [])}
            cols_destino = {c['nombre'].lower(): c for c in destino.esquema[t].get('columnas', [])}
            
            nombres_ori = set(cols_origen.keys())
            nombres_des = set(cols_destino.keys())
            
            cols_nuevas = list(nombres_ori - nombres_des)
            cols_faltantes = list(nombres_des - nombres_ori)
            cols_comunes = list(nombres_ori & nombres_des)
            
            diff_tipos = []
            for c in cols_comunes:
                # Basic comparison
                t_ori = cols_origen[c].get('tipo', '').upper()
                t_des = cols_destino[c].get('tipo', '').upper()
                # Relaxed matching could be done, but for now exact or substring
                if t_ori != t_des and t_ori not in t_des and t_des not in t_ori:
                    diff_tipos.append({'columna': cols_origen[c]['nombre'], 'origen': t_ori, 'destino': t_des})
                    
            if cols_nuevas or cols_faltantes or diff_tipos:
                columnas_modificadas.append({
                    'tabla': t,
                    'nuevas': [cols_origen[c]['nombre'] for c in cols_nuevas],
                    'faltantes': [cols_destino[c]['nombre'] for c in cols_faltantes],
                    'tipos_diferentes': diff_tipos
                })
                
        return jsonify({
            'estado': 'exito',
            'diferencias': {
                'tablas_nuevas': nuevas,
                'tablas_faltantes': faltantes,
                'columnas_modificadas': columnas_modificadas
            }
        })
    except Exception as e:
        return jsonify({'estado': 'error', 'mensaje': f'Error comparando: {str(e)}'})


@principal.route('/api/excluir-tablas', methods=['POST'])
@requerir_login
def api_excluir_tablas():
    """Recibe la lista de tablas que el usuario desmarcó para no migrar."""
    datos = request.json or {}
    excluidas = datos.get('excluidas', [])
    estado_app['excluidas'] = excluidas
    session['excluidas'] = excluidas
    return jsonify({'estado': 'exito'})

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
    session['tipo_origen'] = tipo_sugerido
    
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
        session['motor_destino'] = motor
        
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
    
    # Reconstruir estado desde sesión si estamos en un worker distinto
    if not estado_app.get('origen'):
        archivo_actual = session.get('archivo_actual')
        tipo_origen = session.get('tipo_origen')
        if archivo_actual and tipo_origen:
            try:
                ruta = os.path.join(_carpeta_upload_usuario(), archivo_actual)
                if os.path.exists(ruta):
                    origen = ConectorOrigen(ruta, tipo_origen)
                    if origen.tablas:
                        estado_app['origen'] = origen
            except Exception:
                pass
                
    if not estado_app.get('destino'):
        motor_destino = session.get('motor_destino')
        if motor_destino:
            try:
                estado_app['destino'] = CargadorDestino(motor_destino)
            except Exception:
                pass
                
    if 'excluidas' not in estado_app and 'excluidas' in session:
        estado_app['excluidas'] = session['excluidas']

    if not estado_app.get('origen'):
        return jsonify({'estado': 'error', 'mensaje': 'Suba un archivo primero'})
    if not estado_app.get('destino'):
        return jsonify({'estado': 'error', 'mensaje': 'Configure el destino primero'})
    if estado_app.get('proceso_activo'):
        return jsonify({'estado': 'error', 'mensaje': 'Ya hay una migracion en curso'})
    
    datos = request.json or {}
    simulacion = datos.get('simulacion', False)
    
    ip = request.remote_addr or 'desconocida'
    estado_app['proceso_activo'] = True
    estado_app['simulacion'] = simulacion
    estado_app['metricas'] = {'extraidos': 0, 'cargados': 0, 'errores': 0, 'tablas_ok': 0}
    estado_app['_ip_migracion'] = ip  # Guardar IP para el background task
    usuario_id = session.get('usuario_id', 'anonimo')
    estado_app['_usuario_id'] = usuario_id
    
    _registrar_log(f'Iniciando {"simulación de " if simulacion else ""}migracion...', 'info', ip)
    
    socketio.start_background_task(ejecutar_migracion, usuario_id)
    return jsonify({'estado': 'exito'})

def ejecutar_migracion(usuario_id='anonimo'):
    global thread_local
    thread_local.usuario_id = usuario_id
    origen = estado_app.get('origen')
    destino = estado_app.get('destino')
    simulacion = estado_app.get('simulacion', False)
    excluidas = estado_app.get('excluidas', [])
    
    todas_las_tablas = origen.tablas if origen else []
    tablas = [t for t in todas_las_tablas if t not in excluidas]
    total = len(tablas)
    
    # Guardar timestamp de inicio para calcular duración
    estado_app['_fecha_inicio_migracion'] = datetime.now()

    if simulacion:
        _registrar_log('== MODO SIMULACIÓN ACTIVO == (No se escribirán datos reales)', 'info')

    _registrar_log(f'Migrando {total} tablas (Excluidas: {len(excluidas)})...')

    if total == 0:
        _registrar_log('No hay tablas para migrar, pero se procesarán otros objetos (vistas, triggers, etc.)', 'warning')
        socketio.emit('progreso', {
            'porcentaje': 50,
            'tabla': '',
            'estado': 'Procesando otros objetos...',
            'metricas': estado_app['metricas']
        }, skip_sid=None)

    try:
        for idx, tabla in enumerate(tablas):
            if not estado_app['proceso_activo']:
                _registrar_log('Migracion pausada por el usuario', 'warning')
                break

            progreso = int(((idx + 1) / total) * 100) if total > 0 else 100

            try:
                _registrar_log(f'Extrayendo: {tabla}...')
                
                # Iterar sobre chunks (bloques)
                filas_totales_tabla = 0
                for chunk_df in origen.extraer_datos_chunked(tabla, chunksize=10000):
                    filas_chunk = len(chunk_df)
                    estado_app['metricas']['extraidos'] += filas_chunk
                    filas_totales_tabla += filas_chunk

                    if not chunk_df.empty:
                        chunk_df = MapeadorDatos.limpiar_dataframe(chunk_df)
                        
                        if not simulacion:
                            cargados = destino.cargar_tabla(tabla, chunk_df)
                        else:
                            cargados = filas_chunk
                            
                        estado_app['metricas']['cargados'] += cargados

                _registrar_log(f'Tabla {tabla} completada ({filas_totales_tabla} registros).')
                estado_app['metricas']['tablas_ok'] += 1

                socketio.emit('progreso', {
                    'porcentaje': progreso,
                    'tabla': tabla,
                    'estado': f'{tabla}: {filas_totales_tabla} registros migrados' + (' (Simulado)' if simulacion else ''),
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
                duracion_seg = (ahora - (estado_app.get('_fecha_inicio_migracion', ahora))).total_seconds()
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
                    'duracion_segundos': duracion_seg
                })

                try:
                    from app.auth import run_query
                    run_query(
                        '''INSERT INTO historial_migraciones 
                        (usuario_id, motor_origen, motor_destino, tablas_migradas, registros_migrados, errores, duracion_segundos, fecha) 
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?)''',
                        (
                            usuario_id if usuario_id != 'anonimo' else None,
                            os.path.basename(origen.ruta) if getattr(origen, 'ruta', None) else '',
                            destino.motor if destino else 'Desconocido',
                            estado_app['metricas'].get('tablas_ok', 0),
                            estado_app['metricas'].get('cargados', 0),
                            estado_app['metricas'].get('errores', 0),
                            duracion_seg,
                            ahora.strftime('%Y-%m-%d %H:%M:%S')
                        ),
                        commit=True
                    )
                except Exception as e_db:
                    _registrar_log(f'Error guardando en BD historial: {str(e_db)}', 'error')

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

@principal.route('/api/descargar-reporte')
@requerir_login
def api_descargar_reporte():
    """Genera un reporte de auditoría en Excel."""
    _registrar_actividad_ip('Descargar reporte auditoria')
    metricas = estado_app.get('metricas', {})
    if not metricas:
        return jsonify({'estado': 'error', 'mensaje': 'No hay datos de migracion recientes'})
        
    import pandas as pd
    from io import BytesIO
    from datetime import datetime
    
    origen = estado_app.get('origen')
    destino = estado_app.get('destino')
    inicio = estado_app.get('_fecha_inicio_migracion', datetime.now())
    fin = datetime.now()
    duracion = str(fin - inicio).split('.')[0]
    simulacion = estado_app.get('simulacion', False)
    
    resumen = {
        'Métrica': [
            'Fecha del Reporte', 'Modo', 'Motor Origen', 'Motor Destino', 
            'Duración', 'Total Tablas', 'Filas Extraidas', 
            'Filas Cargadas', 'Errores Detectados'
        ],
        'Valor': [
            fin.strftime("%Y-%m-%d %H:%M:%S"),
            'Simulación (Dry Run)' if simulacion else 'Migración Real',
            getattr(origen, 'tipo', 'Desconocido') if origen else '-',
            getattr(destino, 'motor', 'Desconocido') if destino else '-',
            duracion,
            metricas.get('tablas_ok', 0),
            metricas.get('extraidos', 0),
            metricas.get('cargados', 0),
            metricas.get('errores', 0)
        ]
    }
    
    df_resumen = pd.DataFrame(resumen)
    
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df_resumen.to_excel(writer, sheet_name='Resumen', index=False)
        worksheet = writer.sheets['Resumen']
        worksheet.column_dimensions['A'].width = 25
        worksheet.column_dimensions['B'].width = 30
        
    output.seek(0)
    
    return send_file(
        output,
        as_attachment=True,
        download_name=f"Reporte_Migracion_{fin.strftime('%Y%m%d_%H%M%S')}.xlsx",
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )

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
    # Intentar reconstruir si el worker no tiene estado
    if not estado_app.get('origen'):
        archivo_actual = session.get('archivo_actual')
        tipo_origen = session.get('tipo_origen')
        if archivo_actual and tipo_origen:
            try:
                ruta = os.path.join(_carpeta_upload_usuario(), archivo_actual)
                if os.path.exists(ruta):
                    origen = ConectorOrigen(ruta, tipo_origen)
                    if origen.tablas:
                        estado_app['origen'] = origen
            except Exception:
                pass
                
    if not estado_app.get('destino'):
        motor_destino = session.get('motor_destino')
        if motor_destino:
            try:
                estado_app['destino'] = CargadorDestino(motor_destino)
            except Exception:
                pass

    if estado_app.get('origen'):
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
    try:
        from app.auth import run_query
        usuario_id = session.get('usuario_id')
        res = run_query(
            '''SELECT id, fecha, motor_origen, motor_destino, tablas_migradas, registros_migrados, errores, duracion_segundos 
               FROM historial_migraciones 
               WHERE usuario_id = ? OR usuario_id IS NULL 
               ORDER BY fecha DESC LIMIT 50''',
            (usuario_id,),
            fetchall=True
        )
        historial_db = []
        if res:
            for row in res:
                historial_db.append({
                    'id': row[0],
                    'timestamp': row[1],
                    'archivo_origen': row[2],
                    'motor_destino': row[3],
                    'metricas': {
                        'tablas_ok': row[4],
                        'cargados': row[5],
                        'errores': row[6]
                    },
                    'duracion_segundos': row[7]
                })
        resp = jsonify({'estado': 'exito', 'historial': historial_db, 'logs': estado_app['logs']})
    except Exception as e:
        if not estado_app['historial']:
            return jsonify({'estado': 'error', 'mensaje': 'Error leyendo base de datos'}), 500
        historial_ordenado = sorted(
            estado_app['historial'],
            key=lambda x: x.get('timestamp', x.get('fecha', '')),
            reverse=True
        )
        resp = jsonify({'estado': 'exito', 'historial': historial_ordenado, 'logs': estado_app['logs']})
    # Sin caché para datos en tiempo real
    resp.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    resp.headers['Pragma'] = 'no-cache'
    resp.headers['Expires'] = '0'
    return resp

@principal.route('/api/ips')
def api_ips():
    return jsonify({'ips': estado_app['ips']})

# ==================== RUTAS DE PERFIL ====================

@principal.route('/perfil', methods=['GET'])
@requerir_login
def perfil():
    """Muestra el perfil del usuario actual."""
    from app.auth import obtener_perfil_usuario
    usuario_id = session.get('usuario_id')
    perfil_data = obtener_perfil_usuario(usuario_id)
    
    if not perfil_data:
        return redirect(url_for('principal.login'))
    
    from app.auth import run_query
    
    seguidores = run_query('SELECT COUNT(*) FROM comunidad_seguidores WHERE seguido_id = ?', (usuario_id,), fetchone=True)[0] or 0
    seguidos = run_query('SELECT COUNT(*) FROM comunidad_seguidores WHERE seguidor_id = ?', (usuario_id,), fetchone=True)[0] or 0
    
    usuario_actual = obtener_usuario_actual()
    return render_template('perfil.html', perfil=perfil_data, usuario=usuario_actual, seguidores=seguidores, seguidos=seguidos)

@principal.route('/usuario/foto')
@requerir_login
def foto_perfil_route():
    """Sirve la foto de perfil del usuario actual desde la base de datos."""
    from app.auth import obtener_perfil_usuario
    import base64
    from flask import current_app
    
    usuario_id = session.get('usuario_id')
    perfil = obtener_perfil_usuario(usuario_id)
    if perfil and perfil.get('foto_perfil'):
        data = perfil['foto_perfil']
        if ',' in data:
            header, encoded = data.split(',', 1)
            mime = header.split(':')[1].split(';')[0]
            try:
                decoded = base64.b64decode(encoded)
                return current_app.response_class(decoded, mimetype=mime)
            except Exception:
                pass
    return '', 404

@principal.route('/perfil/actualizar', methods=['POST'])
@requerir_login
def actualizar_perfil():
    """Actualiza el perfil del usuario (foto y descripción)."""
    from app.auth import actualizar_perfil_usuario, obtener_perfil_usuario
    
    usuario_id = session.get('usuario_id')
    descripcion = request.form.get('descripcion', '').strip()
    github_url = request.form.get('github_url', '').strip()
    
    # Limitar descripción a 500 caracteres
    if len(descripcion) > 500:
        descripcion = descripcion[:500]
    
    # Procesar foto de perfil si se subió
    foto_perfil = None
    if 'foto' in request.files:
        archivo = request.files['foto']
        if archivo and archivo.filename != '':
            # Validar que sea una imagen
            extensiones_permitidas = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
            if '.' in archivo.filename:
                ext = archivo.filename.rsplit('.', 1)[1].lower()
                if ext in extensiones_permitidas:
                    # Leer archivo y convertir a base64
                    contenido = archivo.read()
                    foto_perfil = base64.b64encode(contenido).decode('utf-8')
                    # Agregar prefijo para data URI
                    mime_type = f'image/{ext}' if ext != 'jpg' else 'image/jpeg'
                    foto_perfil = f'data:{mime_type};base64,{foto_perfil}'
    
    # Actualizar perfil
    exito, mensaje = actualizar_perfil_usuario(usuario_id, foto_perfil, descripcion, github_url=github_url if github_url else None)
    
    if exito:
        perfil_actualizado = obtener_perfil_usuario(usuario_id)
        session['tiene_foto'] = bool(perfil_actualizado and perfil_actualizado.get('foto_perfil'))
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        # AJAX request
        if exito:
            return jsonify({'estado': 'exito', 'mensaje': mensaje})
        else:
            return jsonify({'estado': 'error', 'mensaje': mensaje}), 400
    else:
        # Form submission
        if exito:
            _registrar_log(f'Usuario {session.get("usuario")} actualizó su perfil', 'info', request.remote_addr)
            import time
            return redirect(url_for('principal.perfil', t=int(time.time())))
        else:
            perfil_data = obtener_perfil_usuario(usuario_id)
            usuario_actual = obtener_usuario_actual()
            return render_template('perfil.html', perfil=perfil_data, usuario=usuario_actual, error=mensaje)

@principal.route('/cli')
@requerir_login
def cli_page():
    return render_template('cli.html')



@socketio.on('conectar')
def conectar():
    socketio.emit('log', {'mensaje': 'Sistema listo. Suba un archivo para comenzar.'})

# =====================================================================
# COMUNIDAD
# =====================================================================

@principal.route('/comunidad')
@requerir_login
def comunidad():
    """Renderiza la vista principal de la comunidad."""
    _registrar_actividad_ip('Vista Comunidad')
    return render_template('comunidad.html')

@principal.route('/api/comunidad/posts', methods=['GET'])
@requerir_login
def api_obtener_posts():
    """Obtiene los posts de la comunidad con datos del autor."""
    try:
        from app.auth import run_query
        usuario_id = session.get('usuario_id')
        # Traer posts ordenados por fecha descendente con métricas sociales
        query = '''
            SELECT p.id, p.titulo, p.contenido, p.tipo, p.creado_en, 
                   u.id, u.usuario, u.foto_perfil,
                   (SELECT COUNT(*) FROM comunidad_likes WHERE post_id = p.id),
                   (SELECT COUNT(*) FROM comunidad_comentarios WHERE post_id = p.id),
                   (SELECT COUNT(*) FROM comunidad_likes WHERE post_id = p.id AND usuario_id = ?),
                   p.resuelto
            FROM comunidad_posts p
            JOIN usuarios u ON p.usuario_id = u.id
            ORDER BY p.creado_en DESC
            LIMIT 50
        '''
        res = run_query(query, (usuario_id,), fetchall=True)
        posts = []
        if res:
            for row in res:
                posts.append({
                    'id': row[0],
                    'titulo': row[1],
                    'contenido': row[2],
                    'tipo': row[3],
                    'creado_en': row[4],
                    'autor_id': row[5],
                    'autor': row[6],
                    'foto_perfil': row[7] or 'https://ui-avatars.com/api/?name=' + row[6] + '&background=random',
                    'likes': row[8],
                    'comentarios': row[9],
                    'liked': bool(row[10]),
                    'resuelto': bool(row[11])
                })
        return jsonify({'estado': 'exito', 'posts': posts})
    except Exception as e:
        return jsonify({'estado': 'error', 'mensaje': str(e)})

@principal.route('/api/comunidad/posts', methods=['POST'])
@requerir_login
def api_crear_post():
    """Crea un nuevo post en la comunidad."""
    datos = request.json or {}
    titulo = datos.get('titulo', '').strip()
    contenido = datos.get('contenido', '').strip()
    tipo = datos.get('tipo', 'tip').strip()
    
    if not titulo or not contenido:
        return jsonify({'estado': 'error', 'mensaje': 'Título y contenido son obligatorios.'})
        
    usuario_id = session.get('usuario_id')
    if not usuario_id:
        return jsonify({'estado': 'error', 'mensaje': 'No autorizado.'}), 401
        
    try:
        from app.auth import run_query
        run_query('''
            INSERT INTO comunidad_posts (usuario_id, titulo, contenido, tipo)
            VALUES (?, ?, ?, ?)
        ''', (usuario_id, titulo, contenido, tipo), commit=True)
        from app import socketio
        socketio.emit('actualizar_comunidad')
        return jsonify({'estado': 'exito', 'mensaje': 'Post creado correctamente.'})
    except Exception as e:
        return jsonify({'estado': 'error', 'mensaje': str(e)})

@principal.route('/api/comunidad/posts/<int:post_id>/like', methods=['POST'])
@requerir_login
def api_toggle_like(post_id):
    """Agrega o quita el like de un post para el usuario actual."""
    usuario_id = session.get('usuario_id')
    try:
        from app.auth import run_query
        # Verificar si ya existe
        existe = run_query('SELECT id FROM comunidad_likes WHERE post_id = ? AND usuario_id = ?', (post_id, usuario_id), fetchone=True)
        from app import socketio
        if existe:
            run_query('DELETE FROM comunidad_likes WHERE post_id = ? AND usuario_id = ?', (post_id, usuario_id), commit=True)
            socketio.emit('actualizar_comunidad')
            return jsonify({'estado': 'exito', 'accion': 'unliked'})
        else:
            run_query('INSERT INTO comunidad_likes (post_id, usuario_id) VALUES (?, ?)', (post_id, usuario_id), commit=True)
            socketio.emit('actualizar_comunidad')
            return jsonify({'estado': 'exito', 'accion': 'liked'})
    except Exception as e:
        return jsonify({'estado': 'error', 'mensaje': str(e)})

@principal.route('/api/comunidad/posts/<int:post_id>/comentarios', methods=['GET', 'POST'])
@requerir_login
def api_comentarios(post_id):
    """Obtiene o agrega comentarios a un post."""
    from app.auth import run_query
    usuario_id = session.get('usuario_id')
    
    if request.method == 'POST':
        datos = request.json or {}
        contenido = datos.get('contenido', '').strip()
        if not contenido:
            return jsonify({'estado': 'error', 'mensaje': 'El comentario no puede estar vacío.'})
        try:
            run_query('''
                INSERT INTO comunidad_comentarios (post_id, usuario_id, contenido)
                VALUES (?, ?, ?)
            ''', (post_id, usuario_id, contenido), commit=True)
            from app import socketio
            socketio.emit('actualizar_comentarios', {'post_id': post_id})
            socketio.emit('actualizar_comunidad')
            return jsonify({'estado': 'exito', 'mensaje': 'Comentario agregado.'})
        except Exception as e:
            return jsonify({'estado': 'error', 'mensaje': str(e)})
            
    else:
        try:
            query = '''
                SELECT c.id, c.contenido, c.creado_en, u.id, u.usuario, u.foto_perfil
                FROM comunidad_comentarios c
                JOIN usuarios u ON c.usuario_id = u.id
                WHERE c.post_id = ?
                ORDER BY c.creado_en ASC
            '''
            res = run_query(query, (post_id,), fetchall=True)
            comentarios = []
            if res:
                for row in res:
                    comentarios.append({
                        'id': row[0],
                        'contenido': row[1],
                        'creado_en': row[2],
                        'autor_id': row[3],
                        'autor': row[4],
                        'foto_perfil': row[5] or 'https://ui-avatars.com/api/?name=' + row[4] + '&background=random'
                    })
            return jsonify({'estado': 'exito', 'comentarios': comentarios})
        except Exception as e:
            return jsonify({'estado': 'error', 'mensaje': str(e)})

@principal.route('/api/usuarios/<int:target_id>/perfil', methods=['GET'])
@requerir_login
def api_obtener_perfil(target_id):
    """Obtiene el perfil de un usuario y si lo sigo."""
    usuario_id = session.get('usuario_id')
    try:
        from app.auth import run_query
        query = '''
            SELECT 
                u.id, u.usuario, u.descripcion, u.foto_perfil,
                (SELECT COUNT(*) FROM comunidad_seguidores WHERE seguido_id = u.id) AS seguidores,
                (SELECT COUNT(*) FROM comunidad_seguidores WHERE seguidor_id = u.id) AS seguidos,
                (SELECT COUNT(*) FROM comunidad_seguidores WHERE seguidor_id = ? AND seguido_id = u.id) AS lo_sigo
            FROM usuarios u
            WHERE u.id = ?
        '''
        user_res = run_query(query, (usuario_id, target_id), fetchone=True)
        if not user_res:
            return jsonify({'estado': 'error', 'mensaje': 'Usuario no encontrado'})
            
        perfil = {
            'id': user_res[0],
            'usuario': user_res[1],
            'descripcion': user_res[2] or 'Sin descripción.',
            'foto_perfil': user_res[3] or 'https://ui-avatars.com/api/?name=' + user_res[1] + '&background=random',
            'seguidores': user_res[4],
            'seguidos': user_res[5],
            'lo_sigo': bool(user_res[6]),
            'es_mi_perfil': usuario_id == target_id
        }
        return jsonify({'estado': 'exito', 'perfil': perfil})
    except Exception as e:
        return jsonify({'estado': 'error', 'mensaje': str(e)})

@principal.route('/api/usuarios/<int:target_id>/seguir', methods=['POST'])
@requerir_login
def api_toggle_seguir(target_id):
    """Permite seguir o dejar de seguir a un usuario."""
    usuario_id = session.get('usuario_id')
    if usuario_id == target_id:
        return jsonify({'estado': 'error', 'mensaje': 'No puedes seguirte a ti mismo'})
        
    try:
        from app.auth import run_query
        existe = run_query('SELECT id FROM comunidad_seguidores WHERE seguidor_id = ? AND seguido_id = ?', (usuario_id, target_id), fetchone=True)
        if existe:
            run_query('DELETE FROM comunidad_seguidores WHERE seguidor_id = ? AND seguido_id = ?', (usuario_id, target_id), commit=True)
            return jsonify({'estado': 'exito', 'accion': 'unfollowed'})
        else:
            run_query('INSERT INTO comunidad_seguidores (seguidor_id, seguido_id) VALUES (?, ?)', (usuario_id, target_id), commit=True)
            return jsonify({'estado': 'exito', 'accion': 'followed'})
    except Exception as e:
        return jsonify({'estado': 'error', 'mensaje': str(e)})

@principal.route('/api/comunidad/posts/<int:post_id>', methods=['DELETE'])
@requerir_login
def api_eliminar_post(post_id):
    """Elimina un post si el usuario activo es el autor."""
    usuario_id = session.get('usuario_id')
    try:
        from app.auth import run_query
        # Verificar si el post existe y el autor es el correcto
        post = run_query('SELECT usuario_id FROM comunidad_posts WHERE id = ?', (post_id,), fetchone=True)
        if not post:
            return jsonify({'estado': 'error', 'mensaje': 'Post no encontrado.'}), 404
            
        if post[0] != usuario_id:
            # Check if admin
            rol = run_query('SELECT rol FROM usuarios WHERE id = ?', (usuario_id,), fetchone=True)
            if not rol or rol[0] != 'admin':
                return jsonify({'estado': 'error', 'mensaje': 'No tienes permiso para eliminar este post.'}), 403
                
        # Eliminar el post (en MySQL las FKs con CASCADE borrarán likes y comments)
        # En SQLite a menos que PRAGMA foreign_keys = ON, debemos borrarlos manualmente
        from app.auth import USE_MYSQL
        if not USE_MYSQL:
            run_query('DELETE FROM comunidad_likes WHERE post_id = ?', (post_id,), commit=True)
            run_query('DELETE FROM comunidad_comentarios WHERE post_id = ?', (post_id,), commit=True)
            
        run_query('DELETE FROM comunidad_posts WHERE id = ?', (post_id,), commit=True)
        
        from app import socketio
        socketio.emit('actualizar_comunidad')
        return jsonify({'estado': 'exito', 'mensaje': 'Post eliminado.'})
    except Exception as e:
        return jsonify({'estado': 'error', 'mensaje': str(e)})

@principal.route('/api/comunidad/posts/<int:post_id>/resolver', methods=['POST'])
@requerir_login
def api_resolver_post(post_id):
    """Marca un post como resuelto si el usuario activo es el autor."""
    usuario_id = session.get('usuario_id')
    try:
        from app.auth import run_query
        # Verificar si el post existe y el autor es el correcto
        post = run_query('SELECT usuario_id, tipo FROM comunidad_posts WHERE id = ?', (post_id,), fetchone=True)
        if not post:
            return jsonify({'estado': 'error', 'mensaje': 'Post no encontrado.'}), 404
            
        if post[0] != usuario_id:
            return jsonify({'estado': 'error', 'mensaje': 'No tienes permiso para resolver este post.'}), 403
            
        if post[1] != 'pregunta':
            return jsonify({'estado': 'error', 'mensaje': 'Solo las preguntas (Dudas) pueden marcarse como resueltas.'}), 400
            
        run_query('UPDATE comunidad_posts SET resuelto = 1 WHERE id = ?', (post_id,), commit=True)
        
        from app import socketio
        socketio.emit('actualizar_comunidad')
        return jsonify({'estado': 'exito', 'mensaje': 'Post marcado como resuelto.'})
    except Exception as e:
        return jsonify({'estado': 'error', 'mensaje': str(e)})