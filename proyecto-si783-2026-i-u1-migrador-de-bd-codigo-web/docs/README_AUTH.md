# MigradorBD - Sistema de Autenticación Completo

Sistema de migración de bases de datos con autenticación segura (usuario/contraseña, Google OAuth, Apple OAuth) y control de roles (admin y usuario regular).

## Características

✅ **Autenticación Tradicional**
- Registro de usuarios con validación
- Inicio de sesión seguro con hash de contraseñas
- Gestión de sesiones seguras

✅ **OAuth 2.0 Integrado**
- Login con Google
- Login con GitHub
- Creación automática de cuentas

✅ **Sistema de Roles**
- **Usuario Regular**: Acceso a migración e historial
- **Admin**: Acceso total + panel de administración + monitoreo IP

✅ **Funcionalidades Adicionales**
- Creación de nuevos admins (solo por admins)
- Cierre de sesión seguro
- Navegación dinámica según rol

## Instalación

### 1. Clonar o descargar el proyecto

```bash
cd proyecto-si783-2026-i-u1-migrador-de-bd-codigo-web
```

### 2. Crear entorno virtual (recomendado)

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

### 3. Instalar dependencias

```bash
pip install -r requirements.txt
```

### 4. Configurar variables de entorno

```bash
# Copiar archivo de ejemplo
cp .env.example .env

# Editar .env y agregar tus credenciales OAuth
# Ver OAUTH_SETUP.md para instrucciones detalladas
```

### 5. Iniciar la aplicación

```bash
python run.py
```

La aplicación estará disponible en: `http://localhost:5000`

## Estructura del Proyecto

```
proyecto/
├── app/
│   ├── __init__.py         # Inicialización Flask
│   ├── auth.py             # Sistema de autenticación y roles
│   ├── oauth.py            # Configuración OAuth
│   ├── routes.py           # Rutas y endpoints
│   ├── static/
│   │   ├── css/
│   │   │   └── estilo.css
│   │   └── js/
│   │       └── main.js
│   └── templates/
│       ├── base.html       # Template base
│       ├── login.html      # Login con OAuth
│       ├── registro.html   # Registro
│       ├── admin.html      # Panel admin
│       ├── migracion.html  # Migración
│       ├── historial.html  # Historial
│       └── monitoreo_ip.html
├── config.py               # Configuración centralizada
├── run.py                  # Punto de entrada
├── auth.db                 # BD de usuarios (se crea automáticamente)
├── .env                    # Variables de entorno (NO commitar)
├── .env.example            # Plantilla de .env
├── requirements.txt        # Dependencias Python
├── AUTENTICACION.md        # Doc. autenticación tradicional
├── OAUTH_SETUP.md          # Doc. configuración OAuth
└── README.md               # Este archivo
```

## Primeros Pasos

### Sin credenciales OAuth (desarrollo local)

1. Inicia la aplicación: `python run.py`
2. Ve a `http://localhost:5000/login`
3. Usa credenciales por defecto:
   - **Usuario**: `admin`
   - **Contraseña**: `admin123`
4. Regístrate como usuario regular si lo deseas

### Con credenciales OAuth

Sigue las instrucciones en `OAUTH_SETUP.md`:

1. **Google**:
   - Ve a [Google Cloud Console](https://console.cloud.google.com/)
   - Crea un proyecto y obtén credenciales OAuth
   - Copia ID y Secret a `.env`

2. **GitHub**:
   - Ve a [GitHub Developer Settings](https://github.com/settings/developers)
   - Crea una OAuth App
   - Copia Client ID y Client Secret a `.env`

3. Reinicia la aplicación
4. Los botones de Google y GitHub aparecerán en la pantalla de login

## Base de Datos

### Usuarios Locales

Tabla: `usuarios`
```sql
- id (INTEGER PRIMARY KEY)
- usuario (TEXT UNIQUE) - Nombre de usuario
- email (TEXT UNIQUE) - Email
- contraseña (TEXT) - Hash bcrypt
- rol (TEXT) - 'admin' o 'usuario'
- creado_en (TIMESTAMP)
- activo (BOOLEAN)
```

### OAuth Linkage

Tabla: `oauth_usuarios`
```sql
- id (INTEGER PRIMARY KEY)
- usuario_id (INTEGER FK)
- proveedor (TEXT) - 'google' o 'apple'
- proveedor_id (TEXT) - ID del proveedor
- email (TEXT)
- nombre (TEXT)
- foto_url (TEXT)
- creado_en (TIMESTAMP)
```

## Flujos de Autenticación

### 1. Registro Tradicional
```
usuario → /registro → registra usuario → /login → inicia sesión → /migracion
```

### 2. Login Tradicional
```
usuario → /login → ingresa credenciales → /migracion
```

### 3. Google OAuth
```
usuario → clic en "Google" → Google Consent Screen → /auth/google/callback → crea/actualiza usuario → /migracion
```

### 4. GitHub OAuth
```
usuario → clic en "GitHub" → GitHub Auth Screen → /auth/github/callback → crea/actualiza usuario → /migracion
```

## Seguridad

### Contraseñas
- Hash con `werkzeug.security` (sha256 con salt)
- Nunca se almacenan en texto plano

### Sesiones
- HttpOnly cookies (no accesibles desde JavaScript)
- SameSite=Lax (protección CSRF)
- SECURE en producción (solo HTTPS)

### OAuth
- Tokens verificados en cada callback
- ID tokens decodificados de forma segura
- Información del usuario guardada en BD

### Roles
- Decoradores `@requerir_login` y `@requerir_admin`
- Verificación en cada petición
- Monitoreo IP solo para admins

## Variables de Entorno

```bash
# Flask
SECRET_KEY=tu-clave-secreta-segura
SESSION_COOKIE_SECURE=False  # True en producción

# Google OAuth
GOOGLE_CLIENT_ID=xxx.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=xxx

# GitHub OAuth
GITHUB_CLIENT_ID=xxx
GITHUB_CLIENT_SECRET=xxx
```

## Troubleshooting

### "ModuleNotFoundError: No module named 'authlib'"
```bash
pip install authlib
```

### "No module named 'dotenv'"
```bash
pip install python-dotenv
```

### OAuth buttons no aparecen
- Verifica que `.env` esté configurado
- Reinicia la aplicación
- Revisa la consola de JavaScript del navegador

### "Invalid redirect URI" en Google/Apple
- Verifica que la URL esté registrada exactamente
- Incluye protocolo y puerto
- En producción, usa HTTPS

### Usuario no se crea con OAuth
- Revisa los logs en consola
- Verifica credenciales en `.env`
- Comprueba que el callback URL es correcto

## Cambios de Producción

Para pasar a producción:

1. **HTTPS obligatorio**
   ```python
   SESSION_COOKIE_SECURE = True
   ```

2. **SECRET_KEY segura**
   ```bash
   python -c "import secrets; print(secrets.token_hex(32))"
   ```

3. **Base de datos robusta**
   - Cambiar de SQLite a PostgreSQL o MySQL

4. **OAuth URLs**
   - Registrar dominio en Google/Apple
   - Usar URLs de producción en callbacks

5. **Verificación JWT**
   - Implementar verificación completa de firma
   - Validar timing de tokens

6. **Logging**
   - Guardar logs en archivo/servicio
   - Monitorear intentos fallidos

## Documentación Adicional

- `AUTENTICACION.md` - Sistema de autenticación tradicional
- `OAUTH_SETUP.md` - Configuración detallada de OAuth

## Licencia

Proyecto de la UPT - Facultad de Ingeniería

## Soporte

Para problemas o preguntas, revisa:
1. Los archivos .md de documentación
2. Los logs de la aplicación
3. La consola del navegador (F12)
