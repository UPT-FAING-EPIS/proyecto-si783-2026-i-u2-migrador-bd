# Sistema de Autenticación y Roles - MigradorBD

## Cambios Realizados

Se ha implementado un sistema completo de autenticación con roles (admin y usuario) para proteger el sistema de migración de bases de datos.

### 1. **Módulo de Autenticación** (`app/auth.py`)
- Sistema de registro e inicio de sesión
- Almacenamiento seguro de contraseñas (hash con werkzeug)
- Decoradores para proteger rutas por autenticación y rol
- Creación de admin por defecto al inicializar la BD
- Base de datos SQLite para usuarios

### 2. **Rutas de Autenticación** (en `app/routes.py`)
- `/login` - Página de inicio de sesión
- `/registro` - Página de registro para nuevos usuarios
- `/logout` - Cierre de sesión
- `/admin` - Panel de administración (solo para admins)
  - Crear nuevos administradores
  - Ver lista de usuarios registrados

### 3. **Rutas Protegidas**
Todas las rutas de migración ahora requieren autenticación:
- `/migracion` - Protegida con `@requerir_login`
- `/historial` - Protegida con `@requerir_login`
- `/monitoreo-ip` - Protegida con `@requerir_admin` (solo admins)
- Todas las APIs de migración requieren login

### 4. **Interfaz de Usuario Actualizada**

#### Templates Creados:
- `login.html` - Formulario de inicio de sesión
- `registro.html` - Formulario de registro
- `admin.html` - Panel de administración

#### Template Base Actualizado:
- `base.html` - Navegación dinámica según rol
  - Solo admins ven "Monitoreo IP" y "Panel Admin"
  - Muestra usuario actual con su rol
  - Opción de "Salir" para cerrar sesión

### 5. **Flujo de Uso**

#### Primer acceso (sin usuarios):
```
Usuario abre /login
└─ ve opción de registrarse
└─ se registra como usuario regular
└─ inicia sesión
└─ accede a migración y historial
└─ NO ve monitoreo IP (requiere admin)
```

#### Admin por defecto:
```
Usuario: admin
Contraseña: admin123
├─ Tiene acceso a todas las funciones
├─ Ve "Monitoreo IP" y "Panel Admin"
├─ Puede crear nuevos administradores
│  └─ El nuevo admin recibe contraseña temporal
│  └─ Debe cambiarla en primer acceso (futuro)
└─ Ve lista completa de usuarios
```

### 6. **Características de Seguridad**

✓ **Hash de contraseñas** - Usando werkzeug.security
✓ **Sesiones seguras** - HttpOnly cookies
✓ **Decoradores de autorización** - @requerir_login y @requerir_admin
✓ **Base de datos de usuarios** - SQLite local
✓ **Restricción de rutas** - Monitoreo IP solo para admins

### 7. **Cambios en Configuración**

`app/__init__.py`:
- Actualización de SECRET_KEY
- Configuración de cookies de sesión seguras
- HttpOnly y SameSite para mayor protección

## Instrucciones de Prueba

1. **Inicia la aplicación:**
```bash
python run.py
```

2. **Primer acceso:**
   - Abre http://localhost:5000
   - Te redirige automáticamente a `/login`
   - Opción: Registrarse (como usuario regular)
   - O inicia con: usuario=`admin`, contraseña=`admin123`

3. **Como usuario regular:**
   - Solo acceso a Migración, Historial
   - No ve Monitoreo IP

4. **Como admin:**
   - Acceso a todo incluyendo Monitoreo IP
   - Panel Admin para crear otros admins
   - Ve lista de todos los usuarios

## Datos Importantes

- **BD de usuarios:** `auth.db` (creada automáticamente)
- **Admin por defecto:**
  - Usuario: `admin`
  - Contraseña: `admin123`
  - Deberías cambiarla en producción

---

**⚠️ IMPORTANTE PARA PRODUCCIÓN:**
- Cambiar SECRET_KEY en `app/__init__.py`
- Cambiar admin por defecto y su contraseña
- Habilitar HTTPS y establecer SESSION_COOKIE_SECURE = True
- Usar una BD más robusta (PostgreSQL) en lugar de SQLite
