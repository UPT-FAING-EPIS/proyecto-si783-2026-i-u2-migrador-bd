# Funcionalidad de Perfil de Usuario

## Descripción

Se ha implementado un sistema completo de perfil de usuario que permite:

✅ **Ver el perfil del usuario** - Accesible al hacer clic en el nombre de usuario en la barra de navegación
✅ **Cambiar la foto de perfil** - Subir una imagen (PNG, JPG, JPEG, GIF, WebP)
✅ **Agregar/editar descripción** - Hasta 500 caracteres
✅ **Interfaz intuitiva y responsive** - Funciona en desktop y móviles

---

## Cambios Realizados

### 1. **Base de Datos** (app/auth.py)
- ✅ Agregadas columnas `foto_perfil` (LONGTEXT) y `descripcion` (VARCHAR 500)
- ✅ Migración automática para bases de datos existentes
- ✅ Soporta tanto SQLite como MySQL

### 2. **Funciones de Autenticación** (app/auth.py)
```python
# Obtener perfil completo del usuario
obtener_perfil_usuario(usuario_id)
# Retorna: {'id', 'usuario', 'email', 'rol', 'foto_perfil', 'descripcion'}

# Actualizar foto y/o descripción
actualizar_perfil_usuario(usuario_id, foto_perfil=None, descripcion=None)
# Retorna: (exito: bool, mensaje: str)
```

### 3. **Rutas (app/routes.py)**

#### GET `/perfil`
- Muestra el perfil del usuario actual
- Protegida con `@requerir_login`

#### POST `/perfil/actualizar`
- Actualiza foto de perfil y/o descripción
- Acepta multipart/form-data
- Soporta AJAX y form submission

### 4. **Template HTML** (app/templates/perfil.html)
- Diseño moderno con gradiente
- Previsualización de foto antes de subir
- Contador de caracteres en tiempo real
- Totalmente responsive

### 5. **Navegación** (app/templates/base.html)
- Nombre del usuario ahora es clickeable
- Enlace a `/perfil` con hover effect
- Tooltip: "Ver mi perfil"

---

## Cómo Usar

### Para el Usuario Final

1. **Acceder al perfil:**
   - Haz clic en tu nombre de usuario en la barra de navegación (arriba a la derecha)

2. **Cambiar la foto:**
   - Haz clic en el área de "Cambiar Foto de Perfil"
   - Selecciona una imagen (PNG, JPG, JPEG, GIF, WebP)
   - Verás una previsualización antes de guardar

3. **Agregar descripción:**
   - Escribe tu descripción en el campo de texto
   - Máximo 500 caracteres (contador en tiempo real)
   - Por ejemplo: "Especialista en migración de BD SQL", tu ocupación, etc.

4. **Guardar cambios:**
   - Haz clic en "Guardar Cambios"
   - Se guardarán ambos campos de forma segura

---

## Ejemplo de Uso en la Aplicación

```
┌─────────────────────────────────────────────┐
│  MigradorBD      Inicio  Migración  Admin   │
│                        [usuario] [ROL] Salir│
│                             ↑
│                       HAZ CLIC AQUÍ
└─────────────────────────────────────────────┘

               ↓ (Te lleva a)

┌───────────────────────────────────────────────────┐
│                   MI PERFIL                       │
├───────────────────────────────────────────────────┤
│                                                   │
│              [FOTO DE PERFIL]                    │
│                  150x150px                        │
│                                                   │
│  ┌─────────────────────────────────────────────┐ │
│  │ Usuario: juan_perez                         │ │
│  │ Email: juan@example.com                     │ │
│  │ Rol: USUARIO                                │ │
│  └─────────────────────────────────────────────┘ │
│                                                   │
│  ═══ EDITAR PERFIL ═══                           │
│                                                   │
│  [+ Cambiar Foto de Perfil]                      │
│                                                   │
│  Descripción (máximo 500 caracteres)             │
│  ┌─────────────────────────────────────────────┐ │
│  │ Especialista en migración de bases datos... │ │
│  │ SQL Server → PostgreSQL                    │ │
│  └─────────────────────────────────────────────┘ │
│  215/500 caracteres                              │
│                                                   │
│  [Guardar Cambios]  [Cancelar]                   │
│                                                   │
└───────────────────────────────────────────────────┘
```

---

## Detalles Técnicos

### Almacenamiento de Foto
- **Formato:** Data URI con base64 encoding
- **Prefijo:** `data:image/{tipo};base64,{contenido}`
- **Ventajas:** No requiere servidor de archivos separado, escalable

### Validación
- **Extensiones permitidas:** png, jpg, jpeg, gif, webp
- **Tamaño máximo:** Depende del límite de Flask (por defecto 16MB)
- **Descripción:** Máximo 500 caracteres (truncada automáticamente)

### Seguridad
- ✅ Requiere login (`@requerir_login`)
- ✅ Solo el usuario puede actualizar su propio perfil
- ✅ Las imágenes se validan antes de procesar
- ✅ Se registra en logs cada actualización

---

## Archivos Modificados

1. **app/auth.py**
   - Agregadas columnas a tabla `usuarios`
   - Funciones: `obtener_perfil_usuario()`, `actualizar_perfil_usuario()`

2. **app/routes.py**
   - Ruta: `GET /perfil` - Ver perfil
   - Ruta: `POST /perfil/actualizar` - Actualizar perfil

3. **app/templates/perfil.html** ✅ NUEVO
   - Interfaz completa del perfil
   - Formulario de edición
   - Previsualización de imágenes
   - Estilos modernos

4. **app/templates/base.html**
   - Nombre de usuario ahora es enlace clickeable
   - Nuevos estilos CSS para el hover

---

## Próximas Mejoras Sugeridas (Opcionales)

- [ ] Cropping de imagen (recortar foto)
- [ ] Cambio de contraseña desde el perfil
- [ ] Avatar de color personalizado como fallback
- [ ] Validación de lado del servidor (tamaño de imagen)
- [ ] Historial de cambios de perfil
- [ ] Opción de hacer perfil público/privado

---

## Prueba Rápida

```bash
# 1. Iniciar la aplicación
python run.py

# 2. Abrir en navegador
http://localhost:5000/login

# 3. Iniciar sesión

# 4. Hacer clic en el nombre de usuario

# 5. ¡Disfruta de tu nuevo perfil!
```

---

## Notas

- La foto se almacena en base64 en la BD (no se crea archivo)
- Si no subes foto, se muestra un icono de usuario por defecto
- Los cambios se guardan instantáneamente
- El perfil es único por usuario (no hay perfiles públicos por defecto)

**¡Listo para usar!** 🎉
