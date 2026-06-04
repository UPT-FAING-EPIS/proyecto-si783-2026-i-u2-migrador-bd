# Configuración de OAuth - Google y GitHub

## Requisitos de Instalación

```bash
pip install authlib
```

## Configuración de Google OAuth

### 1. Crear proyecto en Google Cloud Console

1. Ve a [Google Cloud Console](https://console.cloud.google.com/)
2. Crea un nuevo proyecto (o selecciona uno existente)
3. Habilita la API: "Google+ API"
4. Ve a "Credenciales" en el menú lateral
5. Haz clic en "Crear credenciales" → "ID de cliente OAuth"
6. Selecciona "Aplicación web"
7. En "URI autorizados de redirección", agrega:
   - `http://localhost:5000/auth/google/callback` (desarrollo)
   - `https://tu-dominio.com/auth/google/callback` (producción)

### 2. Obtener credenciales

- **Client ID**: Copia el "ID de cliente"
- **Client Secret**: Copia el "Secreto de cliente"

### 3. Guardar en variables de entorno

```bash
# En .env
GOOGLE_CLIENT_ID=tu-client-id.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=tu-client-secret
```

---

## Configuración de GitHub OAuth

### 1. Crear OAuth App en GitHub

1. Ve a [GitHub Developer Settings](https://github.com/settings/developers)
2. Haz clic en "New OAuth App" (o "OAuth Apps" → "New OAuth App")
3. Rellena el formulario:
   - **Application name**: "MigradorBD" (o tu nombre)
   - **Homepage URL**: 
     - `http://localhost:5000` (desarrollo)
     - `https://tu-dominio.com` (producción)
   - **Application description**: "Sistema de migración de bases de datos"
   - **Authorization callback URL**:
     - `http://localhost:5000/auth/github/callback` (desarrollo)
     - `https://tu-dominio.com/auth/github/callback` (producción)

### 2. Obtener credenciales

1. Después de crear la app, verás:
   - **Client ID**: Cópialo
   - **Client Secret**: Haz clic en "Generate a new client secret" y cópialo
   
> ⚠️ **Importante**: El Client Secret solo se muestra una vez. Guárdalo en lugar seguro.

### 3. Guardar en variables de entorno

```bash
# En .env
GITHUB_CLIENT_ID=tu-client-id
GITHUB_CLIENT_SECRET=tu-client-secret
```

### 4. Permisos

La aplicación solicita el scope `user:email` que permite:
- Leer el perfil público del usuario
- Acceder a emails (public y private)

---

## Estructura de archivos de configuración

```
proyecto/
├── .env                    # Variables de entorno (NO commitar)
├── .env.example           # Plantilla de variables
├── app/
│   ├── auth.py           # Sistema de autenticación
│   ├── oauth.py          # Configuración OAuth
│   ├── routes.py         # Rutas (con OAuth)
│   └── templates/
│       └── login.html    # Login con botones OAuth
```

## Cómo usar .env

1. Copia `.env.example` a `.env`:
   ```bash
   cp .env.example .env
   ```

2. Rellena tus valores:
   ```
   GOOGLE_CLIENT_ID=...
   GOOGLE_CLIENT_SECRET=...
   GITHUB_CLIENT_ID=...
   GITHUB_CLIENT_SECRET=...
   ```

3. El código carga automáticamente con:
   ```python
   import os
   os.getenv('GOOGLE_CLIENT_ID')
   ```

---

## Base de datos OAuth

Se crea automáticamente una tabla `oauth_usuarios` que guarda:

```sql
CREATE TABLE oauth_usuarios (
    id INTEGER PRIMARY KEY,
    usuario_id INTEGER NOT NULL,      -- Ref a usuarios(id)
    proveedor TEXT NOT NULL,          -- 'google' o 'github'
    proveedor_id TEXT NOT NULL,       -- Sub/ID del proveedor
    email TEXT NOT NULL,
    nombre TEXT,
    foto_url TEXT,
    creado_en TIMESTAMP
);
```

---

## Flujo de autenticación

### Google
```
Usuario hace clic en "Google"
    ↓
Abre ventana de consentimiento de Google
    ↓
Usuario autoriza
    ↓
Redirección a /auth/google/callback con token
    ↓
Sistema verifica token y crea/actualiza usuario
    ↓
Crea sesión y redirige a /migracion
```

### GitHub
```
Usuario hace clic en "GitHub"
    ↓
Abre página de autorización de GitHub
    ↓
Usuario autoriza
    ↓
Redirección a /auth/github/callback con código
    ↓
Sistema intercambia código por token
    ↓
Obtiene información del usuario de GitHub
    ↓
Crea/actualiza usuario en BD
    ↓
Crea sesión y redirige a /migracion
```

---

## Seguridad en Producción

Para producción necesitas:

1. **HTTPS obligatorio**: GitHub y Google requieren conexión segura
2. **Variables de entorno seguras**: Usar servicio como AWS Secrets Manager o similar
3. **Verificación de estado**: Implementar CSRF token en OAuth flow
4. **Token seguro**: Guardar tokens de forma segura (solo en servidor)

---

## Troubleshooting

### "Invalid redirect URI"
- Verifica que la URL de callback esté registrada exactamente
- Incluye el protocolo (http/https)
- Incluye el puerto si es necesario (ej: `:5000`)
- En GitHub, asegúrate de que coincida con "Authorization callback URL"

### "Invalid client"
- Verifica que Client ID y Secret sean correctos
- Asegúrate de que no haya espacios en blanco
- Verifica en `.env` que las variables estén bien configuradas

### "Unauthorized"
- En GitHub, verifica que el token sea válido
- Algunos repos privados pueden requerir permisos adicionales
- Intenta regenerar el Client Secret

### No se obtiene el email de GitHub
- En GitHub, ve a Settings → Developer settings → OAuth Apps
- Verifica que el scope `user:email` esté configurado
- Algunos usuarios de GitHub pueden tener emails privados
- El sistema intenta obtener el email público primero, luego private

### Botones OAuth no aparecen
- Verifica que `.env` esté configurado
- Reinicia la aplicación
- Revisa la consola de JavaScript del navegador (F12)
- Verifica que `python-dotenv` esté instalado: `pip install python-dotenv`

---

## Referencias

- [Google OAuth Documentation](https://developers.google.com/identity/protocols/oauth2)
- [GitHub OAuth Documentation](https://docs.github.com/en/developers/apps/building-oauth-apps)
- [Authlib Documentation](https://docs.authlib.org/)
