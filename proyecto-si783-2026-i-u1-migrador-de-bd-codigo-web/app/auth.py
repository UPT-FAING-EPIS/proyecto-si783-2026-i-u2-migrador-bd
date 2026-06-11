import sqlite3
import os
import traceback
try:
    import mysql.connector
except Exception:
    mysql = None
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
from functools import wraps
from flask import session, redirect, url_for, current_app, jsonify
import secrets
import string
import random
from flask_mail import Message
from app import mail

DB_PATH = os.path.join(os.path.dirname(__file__), '..', 'auth.db')

# Detectar si se debe usar MySQL por variables de entorno
USE_MYSQL = bool(os.getenv('MYSQL_DB'))

# Inicializar pool de conexiones si se usa MySQL
mysql_pool = None
if USE_MYSQL and mysql:
    try:
        from mysql.connector import pooling
        mysql_pool = pooling.MySQLConnectionPool(
            pool_name="migrador_pool",
            pool_size=10,
            pool_reset_session=True,
            host=os.getenv('MYSQL_HOST', 'localhost'),
            port=int(os.getenv('MYSQL_PORT', 3306)),
            user=os.getenv('MYSQL_USER'),
            password=os.getenv('MYSQL_PASSWORD'),
            database=os.getenv('MYSQL_DB')
        )
    except Exception as e:
        print(f"Error inicializando pool de conexiones: {e}")

def get_mysql_conn():
    if mysql_pool:
        return mysql_pool.get_connection()
    return mysql.connector.connect(
        host=os.getenv('MYSQL_HOST', 'localhost'),
        port=int(os.getenv('MYSQL_PORT', 3306)),
        user=os.getenv('MYSQL_USER'),
        password=os.getenv('MYSQL_PASSWORD'),
        database=os.getenv('MYSQL_DB')
    )

def run_query(sql, params=(), fetchone=False, fetchall=False, commit=False, return_lastrowid=False):
    """Ejecuta una consulta en SQLite o MySQL según la configuración.
    - Reemplaza placeholders `?` por `%s` cuando usa MySQL.
    - Retorna filas según fetchone/fetchall o lastrowid si se solicita.
    """
    if USE_MYSQL:
        conn = get_mysql_conn()
        cursor = conn.cursor()
        sql_exec = sql.replace('?', '%s')
        try:
            cursor.execute(sql_exec, params)
            if commit:
                conn.commit()
            if return_lastrowid:
                lr = cursor.lastrowid
                cursor.close()
                conn.close()
                return lr
            if fetchone:
                res = cursor.fetchone()
                cursor.close()
                conn.close()
                return res
            if fetchall:
                res = cursor.fetchall()
                cursor.close()
                conn.close()
                return res
            cursor.close()
            conn.close()
            return None
        except Exception as e:
            try:
                cursor.close()
            except:
                pass
            try:
                conn.close()
            except:
                pass
            raise
    else:
        conn = sqlite3.connect(DB_PATH, timeout=15)
        c = conn.cursor()
        try:
            c.execute(sql, params)
            if commit:
                conn.commit()
            if return_lastrowid:
                lr = c.lastrowid
                conn.close()
                return lr
            if fetchone:
                res = c.fetchone()
                conn.close()
                return res
            if fetchall:
                res = c.fetchall()
                conn.close()
                return res
            conn.close()
            return None
        except Exception:
            conn.close()
            raise

def inicializar_bd():
    """Crea las tablas si no existen y actualiza columnas faltantes."""
    if USE_MYSQL:
        # Asumir que el usuario ya ejecutó el script SQL de creación en MySQL
        try:
            # Comprobar que la tabla usuarios existe
            res = run_query('SELECT COUNT(*) FROM usuarios', fetchone=True)
            if res:
                # Intentar añadir columnas nuevas si faltan (ignorar error si ya existen)
                try:
                    run_query('ALTER TABLE usuarios ADD COLUMN foto_perfil LONGTEXT', commit=True)
                except Exception:
                    pass
                try:
                    run_query('ALTER TABLE usuarios ADD COLUMN descripcion VARCHAR(500)', commit=True)
                except Exception:
                    pass
                
                try:
                    run_query('ALTER TABLE comunidad_posts ADD COLUMN resuelto TINYINT(1) NOT NULL DEFAULT 0', commit=True)
                except Exception:
                    pass
                try:
                    run_query('''
                        CREATE TABLE IF NOT EXISTS comunidad_posts (
                            id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
                            usuario_id INT NOT NULL,
                            titulo VARCHAR(255) NOT NULL,
                            contenido TEXT NOT NULL,
                            tipo VARCHAR(50) NOT NULL,
                            resuelto TINYINT(1) NOT NULL DEFAULT 0,
                            creado_en TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                            FOREIGN KEY (usuario_id) REFERENCES usuarios(id) ON DELETE CASCADE
                        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
                    ''', commit=True)
                    run_query('''
                        CREATE TABLE IF NOT EXISTS comunidad_likes (
                            id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
                            post_id INT NOT NULL,
                            usuario_id INT NOT NULL,
                            creado_en TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                            FOREIGN KEY (post_id) REFERENCES comunidad_posts(id) ON DELETE CASCADE,
                            FOREIGN KEY (usuario_id) REFERENCES usuarios(id) ON DELETE CASCADE,
                            UNIQUE(post_id, usuario_id)
                        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
                    ''', commit=True)
                    run_query('''
                        CREATE TABLE IF NOT EXISTS comunidad_comentarios (
                            id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
                            post_id INT NOT NULL,
                            usuario_id INT NOT NULL,
                            contenido TEXT NOT NULL,
                            creado_en TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                            FOREIGN KEY (post_id) REFERENCES comunidad_posts(id) ON DELETE CASCADE,
                            FOREIGN KEY (usuario_id) REFERENCES usuarios(id) ON DELETE CASCADE
                        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
                    ''', commit=True)
                    run_query('''
                        CREATE TABLE IF NOT EXISTS comunidad_seguidores (
                            id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
                            seguidor_id INT NOT NULL,
                            seguido_id INT NOT NULL,
                            creado_en TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                            FOREIGN KEY (seguidor_id) REFERENCES usuarios(id) ON DELETE CASCADE,
                            FOREIGN KEY (seguido_id) REFERENCES usuarios(id) ON DELETE CASCADE,
                            UNIQUE(seguidor_id, seguido_id)
                        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
                    ''', commit=True)
                    run_query('''
                        CREATE TABLE IF NOT EXISTS historial_migraciones (
                            id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
                            usuario_id INT NOT NULL,
                            fecha TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                            archivo_origen VARCHAR(500),
                            motor_destino VARCHAR(100),
                            tablas_ok INT DEFAULT 0,
                            extraidos INT DEFAULT 0,
                            cargados INT DEFAULT 0,
                            errores INT DEFAULT 0,
                            duracion_segundos FLOAT DEFAULT 0.0,
                            total_tablas INT DEFAULT 0,
                            ip VARCHAR(50),
                            FOREIGN KEY (usuario_id) REFERENCES usuarios(id) ON DELETE CASCADE
                        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
                    ''', commit=True)
                    try:
                        run_query('CREATE INDEX idx_comunidad_likes_post ON comunidad_likes(post_id)', commit=True)
                        run_query('CREATE INDEX idx_comunidad_comentarios_post ON comunidad_comentarios(post_id)', commit=True)
                    except Exception:
                        pass
                except Exception as e:
                    print(f"Error creando comunidad_posts: {e}")
        except Exception:
            # No existe la tabla: intentar crear usando DDL compatible con MySQL
            try:
                run_query('''
                    CREATE TABLE IF NOT EXISTS usuarios (
                        id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
                        usuario VARCHAR(150) NOT NULL UNIQUE,
                        email VARCHAR(255) NOT NULL UNIQUE,
                        contraseña VARCHAR(500),
                        rol VARCHAR(30) NOT NULL DEFAULT 'usuario',
                        creado_en TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                        activo TINYINT(1) NOT NULL DEFAULT 1,
                        verification_code VARCHAR(100),
                        verified TINYINT(1) NOT NULL DEFAULT 0,
                        foto_perfil LONGTEXT,
                        descripcion VARCHAR(500)
                    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
                ''', commit=True)
                run_query('''
                    CREATE TABLE IF NOT EXISTS oauth_usuarios (
                        id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
                        usuario_id INT NOT NULL,
                        proveedor VARCHAR(50) NOT NULL,
                        proveedor_id VARCHAR(255) NOT NULL,
                        email VARCHAR(255) NOT NULL,
                        nombre VARCHAR(255),
                        foto_url TEXT,
                        creado_en TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                        UNIQUE(proveedor, proveedor_id)
                    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
                ''', commit=True)
                run_query('''
                    CREATE TABLE IF NOT EXISTS comunidad_posts (
                        id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
                        usuario_id INT NOT NULL,
                        titulo VARCHAR(255) NOT NULL,
                        contenido TEXT NOT NULL,
                        tipo VARCHAR(50) NOT NULL,
                        resuelto TINYINT(1) NOT NULL DEFAULT 0,
                        creado_en TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (usuario_id) REFERENCES usuarios(id) ON DELETE CASCADE
                    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
                ''', commit=True)
                run_query('''
                    CREATE TABLE IF NOT EXISTS comunidad_likes (
                        id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
                        post_id INT NOT NULL,
                        usuario_id INT NOT NULL,
                        creado_en TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (post_id) REFERENCES comunidad_posts(id) ON DELETE CASCADE,
                        FOREIGN KEY (usuario_id) REFERENCES usuarios(id) ON DELETE CASCADE,
                        UNIQUE(post_id, usuario_id)
                    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
                ''', commit=True)
                run_query('''
                    CREATE TABLE IF NOT EXISTS comunidad_comentarios (
                        id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
                        post_id INT NOT NULL,
                        usuario_id INT NOT NULL,
                        contenido TEXT NOT NULL,
                        creado_en TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (post_id) REFERENCES comunidad_posts(id) ON DELETE CASCADE,
                        FOREIGN KEY (usuario_id) REFERENCES usuarios(id) ON DELETE CASCADE
                    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
                ''', commit=True)
                run_query('''
                    CREATE TABLE IF NOT EXISTS comunidad_seguidores (
                        id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
                        seguidor_id INT NOT NULL,
                        seguido_id INT NOT NULL,
                        creado_en TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (seguidor_id) REFERENCES usuarios(id) ON DELETE CASCADE,
                        FOREIGN KEY (seguido_id) REFERENCES usuarios(id) ON DELETE CASCADE,
                        UNIQUE(seguidor_id, seguido_id)
                    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
                ''', commit=True)
                run_query('''
                    CREATE TABLE IF NOT EXISTS historial_migraciones (
                        id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
                        usuario_id INT NOT NULL,
                        fecha TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                        archivo_origen VARCHAR(500),
                        motor_destino VARCHAR(100),
                        tablas_ok INT DEFAULT 0,
                        extraidos INT DEFAULT 0,
                        cargados INT DEFAULT 0,
                        errores INT DEFAULT 0,
                        duracion_segundos FLOAT DEFAULT 0.0,
                        total_tablas INT DEFAULT 0,
                        ip VARCHAR(50),
                        FOREIGN KEY (usuario_id) REFERENCES usuarios(id) ON DELETE CASCADE
                    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
                ''', commit=True)
                try:
                    run_query('CREATE INDEX idx_comunidad_likes_post ON comunidad_likes(post_id)', commit=True)
                    run_query('CREATE INDEX idx_comunidad_comentarios_post ON comunidad_comentarios(post_id)', commit=True)
                    run_query('CREATE INDEX idx_comunidad_seguidores_seguido ON comunidad_seguidores(seguido_id)', commit=True)
                except Exception:
                    pass
                    
                try:
                    run_query('ALTER TABLE usuarios ADD COLUMN foto_perfil LONGTEXT', commit=True)
                except Exception:
                    pass

                try:
                    run_query('ALTER TABLE usuarios ADD COLUMN descripcion VARCHAR(500)', commit=True)
                except Exception:
                    pass
                    
                try:
                    run_query('ALTER TABLE usuarios ADD COLUMN github_url VARCHAR(255)', commit=True)
                except Exception:
                    pass
            except Exception:
                # Si falla, dejar que el administrador importe el script manualmente
                print('No se pudo crear tablas en MySQL. Importa el script SQL manualmente.')
        # Crear admin por defecto si no existe
        crear_admin_defecto()
    else:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()

        # Crear tabla usuarios si no existe
        c.execute('''
            CREATE TABLE IF NOT EXISTS usuarios (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                usuario TEXT UNIQUE NOT NULL,
                email TEXT UNIQUE NOT NULL,
                contraseña TEXT,
                rol TEXT NOT NULL DEFAULT 'usuario',
                creado_en TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                activo BOOLEAN DEFAULT 1,
                verification_code TEXT,
                verified BOOLEAN DEFAULT 0,
                foto_perfil TEXT,
                descripcion TEXT
            )
        ''')

        # Verificar y agregar columnas faltantes
        c.execute("PRAGMA table_info(usuarios)")
        columns = [column[1] for column in c.fetchall()]

        if 'verification_code' not in columns:
            c.execute("ALTER TABLE usuarios ADD COLUMN verification_code TEXT")

        if 'verified' not in columns:
            c.execute("ALTER TABLE usuarios ADD COLUMN verified BOOLEAN DEFAULT 0")
        
        if 'foto_perfil' not in columns:
            c.execute("ALTER TABLE usuarios ADD COLUMN foto_perfil TEXT")
        
        if 'descripcion' not in columns:
            c.execute("ALTER TABLE usuarios ADD COLUMN descripcion TEXT")

        # Crear tabla oauth_usuarios si no existe
        c.execute('''
            CREATE TABLE IF NOT EXISTS oauth_usuarios (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                usuario_id INTEGER NOT NULL,
                proveedor TEXT NOT NULL,
                proveedor_id TEXT NOT NULL,
                email TEXT NOT NULL,
                nombre TEXT,
                foto_url TEXT,
                creado_en TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (usuario_id) REFERENCES usuarios(id),
                UNIQUE(proveedor, proveedor_id)
            )
        ''')
        
        # Crear tabla comunidad_posts si no existe
        c.execute('''
            CREATE TABLE IF NOT EXISTS comunidad_posts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                usuario_id INTEGER NOT NULL,
                titulo TEXT NOT NULL,
                contenido TEXT NOT NULL,
                tipo TEXT NOT NULL,
                resuelto BOOLEAN DEFAULT 0,
                creado_en TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (usuario_id) REFERENCES usuarios(id)
            )
        ''')
        
        # Verificar columna resuelto en comunidad_posts
        c.execute("PRAGMA table_info(comunidad_posts)")
        cp_columns = [column[1] for column in c.fetchall()]
        if 'resuelto' not in cp_columns:
            c.execute("ALTER TABLE comunidad_posts ADD COLUMN resuelto BOOLEAN DEFAULT 0")

        # Crear tablas sociales (likes, comentarios, seguidores) si no existen
        c.execute('''
            CREATE TABLE IF NOT EXISTS comunidad_likes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                post_id INTEGER NOT NULL,
                usuario_id INTEGER NOT NULL,
                creado_en TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (post_id) REFERENCES comunidad_posts(id),
                FOREIGN KEY (usuario_id) REFERENCES usuarios(id),
                UNIQUE(post_id, usuario_id)
            )
        ''')
        c.execute('''
            CREATE TABLE IF NOT EXISTS comunidad_comentarios (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                post_id INTEGER NOT NULL,
                usuario_id INTEGER NOT NULL,
                contenido TEXT NOT NULL,
                creado_en TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (post_id) REFERENCES comunidad_posts(id),
                FOREIGN KEY (usuario_id) REFERENCES usuarios(id)
            )
        ''')
        c.execute('''
            CREATE TABLE IF NOT EXISTS comunidad_seguidores (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                seguidor_id INTEGER NOT NULL,
                seguido_id INTEGER NOT NULL,
                creado_en TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (seguidor_id) REFERENCES usuarios(id),
                FOREIGN KEY (seguido_id) REFERENCES usuarios(id),
                UNIQUE(seguidor_id, seguido_id)
            )
        ''')
        c.execute('''
            CREATE TABLE IF NOT EXISTS historial_migraciones (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                usuario_id INTEGER NOT NULL,
                fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                archivo_origen TEXT,
                motor_destino TEXT,
                tablas_ok INTEGER DEFAULT 0,
                extraidos INTEGER DEFAULT 0,
                cargados INTEGER DEFAULT 0,
                errores INTEGER DEFAULT 0,
                duracion_segundos REAL DEFAULT 0.0,
                total_tablas INTEGER DEFAULT 0,
                ip TEXT,
                FOREIGN KEY (usuario_id) REFERENCES usuarios(id)
            )
        ''')
        c.execute('CREATE INDEX IF NOT EXISTS idx_comunidad_likes_post ON comunidad_likes(post_id)')
        c.execute('CREATE INDEX IF NOT EXISTS idx_comunidad_comentarios_post ON comunidad_comentarios(post_id)')
        c.execute('CREATE INDEX IF NOT EXISTS idx_comunidad_seguidores_seguido ON comunidad_seguidores(seguido_id)')
        
        # Intentar añadir columna github si no existe en SQLite
        try:
            c.execute('ALTER TABLE usuarios ADD COLUMN github_url VARCHAR(255)')
        except sqlite3.OperationalError:
            pass
            
        conn.commit()
        conn.close()

        # Crear admin por defecto si no existe
        crear_admin_defecto()

def crear_admin_defecto():
    """Crea un admin por defecto si no existe ninguno."""
    try:
        res = run_query('SELECT COUNT(*) FROM usuarios WHERE rol = ?', ('admin',), fetchone=True)
        count = res[0] if res else 0
    except Exception:
        count = 0

    if count == 0:
        contraseña_hash = generate_password_hash('admin123')
        try:
            run_query('INSERT INTO usuarios (usuario, email, contraseña, rol, verified) VALUES (?, ?, ?, ?, ?)',
                      ('admin', 'admin@migrador.local', contraseña_hash, 'admin', 1), commit=True)
        except Exception:
            print('No se pudo insertar admin por defecto. Comprueba el esquema de la BD.')

def enviar_email_verificacion(email, codigo):
    """Envía un email con el código de verificación."""
    try:
        msg = Message('Código de Verificación - MigradorBD',
                      sender=current_app.config['MAIL_DEFAULT_SENDER'],
                      recipients=[email])
        msg.body = f'''Hola,

Tu código de verificación para activar tu cuenta en MigradorBD es: {codigo}

Ingresa este código en la página de verificación para completar tu registro.

Si no solicitaste este registro, ignora este mensaje.

Saludos,
Equipo de MigradorBD
'''
        mail.send(msg)
        return True, None
    except Exception as e:
        error_text = str(e)
        print(f"Error enviando email: {error_text}")
        return False, error_text


def enviar_email_notificacion(email, asunto, mensaje):
    """Envía un email de notificación genérico al usuario."""
    try:
        msg = Message(asunto,
                      sender=current_app.config['MAIL_DEFAULT_SENDER'],
                      recipients=[email])
        msg.body = mensaje
        mail.send(msg)
        return True, None
    except Exception as e:
        error_text = str(e)
        print(f"Error enviando email de notificación: {error_text}")
        return False, error_text


def registrar_usuario(usuario, email, contraseña):
    """Registra un nuevo usuario con rol 'usuario' y envía código de verificación."""
    try:
        # Generar código de verificación
        codigo = ''.join(random.choices(string.digits, k=6))

        contraseña_hash = generate_password_hash(contraseña)
        try:
            run_query('INSERT INTO usuarios (usuario, email, contraseña, rol, verification_code, verified) VALUES (?, ?, ?, ?, ?, ?)',
                      (usuario, email, contraseña_hash, 'usuario', codigo, 0), commit=True)
        except Exception as e:
            return False, str(e)

        # Enviar email de verificación
        enviado, error = enviar_email_verificacion(email, codigo)
        if enviado:
            return True, 'Registro exitoso. Revisa tu email para el código de verificación.'
        else:
            mensaje = 'Registro exitoso, pero no se pudo enviar el email de verificación.'
            if 'Username and Password not accepted' in str(error) or 'BadCredentials' in str(error):
                mensaje += ' Revisa MAIL_USERNAME y MAIL_PASSWORD en .env; usa una contraseña de aplicación de Gmail si corresponde.'
            else:
                mensaje += ' Contacta al administrador.'
            return True, mensaje
    except sqlite3.IntegrityError as e:
        if 'usuario' in str(e):
            return False, 'El usuario ya existe'
        elif 'email' in str(e):
            return False, 'El email ya está registrado'
        return False, 'Error en el registro'
    except Exception as e:
        return False, str(e)

def verificar_usuario(usuario, contraseña):
    """Verifica credenciales y devuelve datos del usuario."""
    try:
        resultado = run_query('SELECT id, usuario, email, rol, activo, verified FROM usuarios WHERE usuario = ?', (usuario,), fetchone=True)

        if not resultado:
            return None

        id_usuario, user, email, rol, activo, verified = resultado

        if not verified:
            return None  # Usuario no verificado

        # Verificar contraseña
        row = run_query('SELECT contraseña FROM usuarios WHERE id = ?', (id_usuario,), fetchone=True)
        contraseña_hash = row[0] if row else None

        if check_password_hash(contraseña_hash, contraseña) and activo:
            return {'id': id_usuario, 'usuario': user, 'email': email, 'rol': rol}
        return None
    except Exception as e:
        return None

def obtener_usuario_por_email(email):
    """Obtiene datos del usuario por email."""
    try:
        resultado = run_query('SELECT id, usuario, email, verified FROM usuarios WHERE email = ?', (email,), fetchone=True)

        if resultado:
            return {'id': resultado[0], 'usuario': resultado[1], 'email': resultado[2], 'verified': resultado[3]}
        return None
    except Exception as e:
        return None

def verificar_codigo(email, codigo):
    """Verifica el código de verificación y activa la cuenta."""
    try:
        resultado = run_query('SELECT id, verification_code FROM usuarios WHERE email = ? AND verified = 0', (email,), fetchone=True)

        if not resultado:
            return False, 'Usuario no encontrado o ya verificado'

        id_usuario, stored_code = resultado

        if stored_code == codigo:
            run_query('UPDATE usuarios SET verified = 1, verification_code = NULL WHERE id = ?', (id_usuario,), commit=True)
            return True, 'Cuenta verificada exitosamente'
        else:
            return False, 'Código incorrecto'
    except Exception as e:
        return False, str(e)

def registrar_usuario_oauth(proveedor, proveedor_id, email, nombre=None, foto_url=None):
    """Registra o actualiza un usuario OAuth."""
    try:
        # Verificar si el usuario ya existe con este proveedor
        resultado = run_query('SELECT usuario_id FROM oauth_usuarios WHERE proveedor = ? AND proveedor_id = ?', (proveedor, proveedor_id), fetchone=True)

        if resultado:
            usuario_id = resultado[0]
            run_query('UPDATE oauth_usuarios SET nombre = ?, foto_url = ? WHERE usuario_id = ? AND proveedor = ?', (nombre, foto_url, usuario_id, proveedor), commit=True)
        else:
            usuario_existente = run_query('SELECT id FROM usuarios WHERE email = ?', (email,), fetchone=True)

            if usuario_existente:
                usuario_id = usuario_existente[0]
            else:
                usuario_generado = nombre or email.split('@')[0]
                usuario_base = usuario_generado
                contador = 1
                while True:
                    exists = run_query('SELECT id FROM usuarios WHERE usuario = ?', (usuario_generado,), fetchone=True)
                    if not exists:
                        break
                    usuario_generado = f"{usuario_base}{contador}"
                    contador += 1

                run_query('INSERT INTO usuarios (usuario, email, rol) VALUES (?, ?, ?)', (usuario_generado, email, 'usuario'), commit=True)
                # Obtener id insertado (varía según driver)
                if USE_MYSQL:
                    # obtener último id
                    usuario_id = run_query('SELECT LAST_INSERT_ID()', fetchone=True)[0]
                else:
                    usuario_id = run_query('SELECT last_insert_rowid()', fetchone=True)[0]

            run_query('INSERT INTO oauth_usuarios (usuario_id, proveedor, proveedor_id, email, nombre, foto_url) VALUES (?, ?, ?, ?, ?, ?)',
                      (usuario_id, proveedor, proveedor_id, email, nombre, foto_url), commit=True)

        return obtener_usuario_por_id(usuario_id)
    except Exception as e:
        return None

def obtener_usuario_por_id(usuario_id):
    """Obtiene datos del usuario por ID."""
    try:
        resultado = run_query('SELECT id, usuario, email, rol FROM usuarios WHERE id = ?', (usuario_id,), fetchone=True)
        if resultado:
            return {'id': resultado[0], 'usuario': resultado[1], 'email': resultado[2], 'rol': resultado[3]}
    except Exception:
        pass
    return None

def requerir_login(f):
    """Decorador para proteger rutas que requieren login."""
    @wraps(f)
    def decorado(*args, **kwargs):
        if 'usuario_id' not in session:
            return redirect(url_for('principal.login'))
        return f(*args, **kwargs)
    return decorado

def requerir_admin(f):
    """Decorador para proteger rutas que requieren rol admin."""
    @wraps(f)
    def decorado(*args, **kwargs):
        if 'usuario_id' not in session:
            return redirect(url_for('principal.login'))

        resultado = run_query('SELECT rol FROM usuarios WHERE id = ?', (session['usuario_id'],), fetchone=True)

        if not resultado or resultado[0] != 'admin':
            return jsonify({'estado': 'error', 'mensaje': 'Solo administradores pueden acceder'}), 403

        return f(*args, **kwargs)
    return decorado

def obtener_usuario_actual():
    """Obtiene los datos del usuario en sesión."""
    if 'usuario_id' not in session:
        return None
    return obtener_usuario_por_id(session['usuario_id'])

def crear_nuevo_admin(usuario_creador_id, usuario_nuevo, email_nuevo):
    """Solo un admin puede crear otro admin."""
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()

        # Verificar que el creador es admin
        c.execute('SELECT rol FROM usuarios WHERE id = ?', (usuario_creador_id,))
        resultado = c.fetchone()
        if not resultado or resultado[0] != 'admin':
            conn.close()
            return False, 'Solo administradores pueden crear otros admins'

        # Generar contraseña temporal
        caracteres = string.ascii_letters + string.digits + "!@#$%"
        contraseña_temporal = ''.join(secrets.choice(caracteres) for _ in range(12))
        contraseña_hash = generate_password_hash(contraseña_temporal)

        c.execute(
            'INSERT INTO usuarios (usuario, email, contraseña, rol) VALUES (?, ?, ?, ?)',
            (usuario_nuevo, email_nuevo, contraseña_hash, 'admin')
        )
        conn.commit()
        conn.close()
        return True, f'Admin creado. Contraseña temporal: {contraseña_temporal}'
    except sqlite3.IntegrityError:
        return False, 'El usuario o email ya existe'
    except Exception as e:
        return False, str(e)

def obtener_perfil_usuario(usuario_id):
    """Obtiene el perfil completo del usuario incluyendo foto y descripción."""
    try:
        resultado = run_query(
            'SELECT id, usuario, email, rol, foto_perfil, descripcion, github_url FROM usuarios WHERE id = ?',
            (usuario_id,),
            fetchone=True
        )
        if resultado:
            return {
                'id': resultado[0],
                'usuario': resultado[1],
                'email': resultado[2],
                'rol': resultado[3],
                'foto_perfil': resultado[4],
                'descripcion': resultado[5],
                'github_url': resultado[6] if len(resultado) > 6 else None
            }
    except Exception as main_e:
        # Fallback si las nuevas columnas no existen aún en la base de datos o hay otro error
        try:
            resultado = run_query(
                'SELECT id, usuario, email, rol FROM usuarios WHERE id = ?',
                (usuario_id,),
                fetchone=True
            )
            if resultado:
                return {
                    'id': resultado[0],
                    'usuario': resultado[1],
                    'email': resultado[2],
                    'rol': resultado[3],
                    'foto_perfil': None,
                    'descripcion': f'ERROR_DB: {str(main_e)}',
                    'github_url': None
                }
        except Exception:
            pass
    return None

def actualizar_perfil_usuario(usuario_id, foto_perfil=None, descripcion=None, github_url=None):
    """Actualiza la foto de perfil, descripción y github del usuario."""
    try:
        if foto_perfil is not None:
            run_query(
                'UPDATE usuarios SET foto_perfil = ? WHERE id = ?',
                (foto_perfil, usuario_id),
                commit=True
            )
        
        if descripcion is not None:
            run_query(
                'UPDATE usuarios SET descripcion = ? WHERE id = ?',
                (descripcion, usuario_id),
                commit=True
            )
            
        if github_url is not None:
            run_query(
                'UPDATE usuarios SET github_url = ? WHERE id = ?',
                (github_url, usuario_id),
                commit=True
            )
            
        return True, 'Perfil actualizado correctamente'
    except Exception as e:
        return False, str(e)
