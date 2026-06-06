![C:\Users\EPIS\Documents\upt.png](media/image1.png){width="1.0879997812773403in" height="1.4625557742782151in"}

**UNIVERSIDAD PRIVADA DE TACNA**

**FACULTAD DE INGENIERIA**

**Escuela Profesional de Ingeniería de Sistemas**

**Proyecto *MigradorBD - Sistema de Migración de Bases de Datos***

Curso: *Ingeniería de Software (SI783)*

Docente: *Mag. Patrick José Cuadros Quiroga*

Integrantes:

***LLica Mamani, Jimmy Mijair***
***Halanocca Rojas, Usher Damiron***

**Tacna – Perú**

***2026***

**\**

<table>
<colgroup>
<col style="width: 10%" />
<col style="width: 12%" />
<col style="width: 15%" />
<col style="width: 16%" />
<col style="width: 11%" />
<col style="width: 33%" />
</colgroup>
<tbody>
<tr>
<td colspan="6" style="text-align: center;">CONTROL DE VERSIONES</td>
</tr>
<tr>
<td style="text-align: center;">Versión</td>
<td style="text-align: center;">Hecha por</td>
<td style="text-align: center;">Revisada por</td>
<td style="text-align: center;">Aprobada por</td>
<td style="text-align: center;">Fecha</td>
<td style="text-align: center;">Motivo</td>
</tr>
<tr>
<td style="text-align: center;">1.0</td>
<td style="text-align: center;">JLM / UHR</td>
<td style="text-align: center;">JLM</td>
<td style="text-align: center;">UHR</td>
<td style="text-align: center;">06/06/2026</td>
<td style="text-align: center;">Versión Original</td>
</tr>
</tbody>
</table>

Sistema *MigradorBD*

Documento de Arquitectura de Software

Versión *1.0*

**\**

<table>
<colgroup>
<col style="width: 10%" />
<col style="width: 12%" />
<col style="width: 15%" />
<col style="width: 16%" />
<col style="width: 11%" />
<col style="width: 33%" />
</colgroup>
<tbody>
<tr>
<td colspan="6" style="text-align: center;">CONTROL DE VERSIONES</td>
</tr>
<tr>
<td style="text-align: center;">Versión</td>
<td style="text-align: center;">Hecha por</td>
<td style="text-align: center;">Revisada por</td>
<td style="text-align: center;">Aprobada por</td>
<td style="text-align: center;">Fecha</td>
<td style="text-align: center;">Motivo</td>
</tr>
<tr>
<td style="text-align: center;">1.0</td>
<td style="text-align: center;">JLM / UHR</td>
<td style="text-align: center;">JLM</td>
<td style="text-align: center;">UHR</td>
<td style="text-align: center;">06/06/2026</td>
<td style="text-align: center;">Versión Original</td>
</tr>
</tbody>
</table>

INDICE GENERAL

# Contenido {#contenido .TOC-Heading}

[1. INTRODUCCIÓN](#introduccion-sad)

[1.1. Propósito (Diagrama 4+1)](#proposito-sad)

[1.2. Alcance](#alcance-sad)

[1.3. Definición, siglas y abreviaturas](#definiciones-sad)

[1.4. Organización del documento](#organizacion-sad)

[2. OBJETIVOS Y RESTRICCIONES ARQUITECTONICAS](#objetivos-restricciones)

[2.1.1. Requerimientos Funcionales](#rf-sad)

[2.1.2. Requerimientos No Funcionales – Atributos de Calidad](#rnf-sad)

[3. REPRESENTACIÓN DE LA ARQUITECTURA DEL SISTEMA](#representacion-arquitectura)

[3.1. Vista de Caso de uso](#vista-caso-uso)

[3.2. Vista Lógica](#vista-logica)

[3.3. Vista de Implementación (vista de desarrollo)](#vista-implementacion)

[3.4. Vista de procesos](#vista-procesos)

[3.5. Vista de Despliegue (vista física)](#vista-despliegue)

[4. ATRIBUTOS DE CALIDAD DEL SOFTWARE](#atributos-calidad)

---

<span id="introduccion-sad"></span>
## 1. INTRODUCCIÓN

<span id="proposito-sad"></span>
### 1.1. Propósito (Diagrama 4+1)

Este documento presenta la arquitectura del sistema MigradorBD utilizando el modelo de vistas 4+1 de Philippe Kruchten. Se describen las vistas de caso de uso, lógica, implementación, procesos y despliegue que conforman la arquitectura completa del sistema.

La arquitectura de MigradorBD se fundamenta en una separación clara de responsabilidades a través de módulos especializados para cada etapa del proceso ETL (Extracción, Transformación y Carga), complementados por una capa de presentación web basada en Flask y una capa de autenticación multi-proveedor.

Las decisiones arquitectónicas priorizan:
- **Modularidad**: Cada etapa del ETL es un módulo independiente.
- **Extensibilidad**: Nuevos motores de base de datos se agregan añadiendo lógica en los módulos existentes.
- **Portabilidad**: El sistema funciona tanto en Windows (threading) como en Linux (eventlet).

<span id="alcance-sad"></span>
### 1.2. Alcance

Este documento cubre la arquitectura del sistema MigradorBD completo, incluyendo:
- La estructura de paquetes y módulos.
- El flujo de datos a través del pipeline ETL.
- La arquitectura de autenticación y autorización.
- La comunicación en tiempo real con WebSocket.
- El despliegue en producción.

<span id="definiciones-sad"></span>
### 1.3. Definición, siglas y abreviaturas

| Sigla | Definición |
|:------|:-----------|
| SAD | Software Architecture Document |
| ETL | Extract, Transform, Load |
| WSGI | Web Server Gateway Interface |
| ORM | Object-Relational Mapping |
| OAuth | Open Authorization |
| WebSocket | Protocolo de comunicación bidireccional sobre TCP |
| Blueprint | Componente modular de Flask para organizar rutas |
| SocketIO | Biblioteca para comunicación WebSocket con fallback |
| SQLAlchemy | Toolkit SQL y ORM para Python |
| Gunicorn | Servidor HTTP WSGI para Python |
| Nginx | Servidor web y proxy reverso |
| Supervisor | Sistema de control de procesos |

<span id="organizacion-sad"></span>
### 1.4. Organización del documento

El documento se organiza siguiendo el modelo 4+1:
1. Objetivos y restricciones arquitectónicas.
2. Vista de caso de uso (escenarios).
3. Vista lógica (clases, paquetes, datos).
4. Vista de implementación (componentes de código).
5. Vista de procesos (flujo del sistema).
6. Vista de despliegue (infraestructura física).
7. Atributos de calidad del software.

---

<span id="objetivos-restricciones"></span>
## 2. OBJETIVOS Y RESTRICCIONES ARQUITECTONICAS

### 2.1. Priorización de requerimientos

| ID | Descripción | Prioridad |
|:---|:-----------|:----------|
| RF-01 | Subir archivos de base de datos (hasta 500 MB) | Alta |
| RF-02 | Detección automática del motor de origen | Alta |
| RF-03 | Extracción completa de esquema y datos | Alta |
| RF-04 | Generación de exportaciones multi-motor | Alta |
| RF-05 | Autenticación con OAuth | Media |
| RF-06 | Integración con GitHub | Baja |
| RNF-01 | Rendimiento: 50 MB en < 60s | Alta |
| RNF-02 | Seguridad: hash scrypt, HttpOnly cookies | Alta |
| RNF-03 | Portabilidad: Windows + Linux | Alta |

<span id="rf-sad"></span>
### 2.1.1. Requerimientos Funcionales

| ID | Descripción | Prioridad |
|:---|:-----------|:----------|
| RF-01 | Subir y procesar archivos de base de datos en múltiples formatos | Alta |
| RF-02 | Detectar automáticamente el tipo de motor SQL (MySQL, PostgreSQL, SQL Server, Oracle, BigQuery, Snowflake, Redshift, Cassandra) | Alta |
| RF-03 | Extraer esquema completo: tablas, columnas, PKs, FKs, índices, vistas, triggers, procedimientos, funciones | Alta |
| RF-04 | Generar exportaciones SQL nativas con tipos de datos traducidos por motor | Alta |
| RF-05 | Generar exportaciones JSON, NDJSON, CQL y Redis | Media |
| RF-06 | Autenticar usuarios con registro local, Google OAuth y GitHub OAuth | Alta |
| RF-07 | Comunicar progreso de migración en tiempo real vía WebSocket | Media |
| RF-08 | Integrar con GitHub (listar repos, crear repos, subir archivos) | Baja |

<span id="rnf-sad"></span>
### 2.1.2. Requerimientos No Funcionales – Atributos de Calidad

| ID | Descripción | Prioridad | Categoría |
|:---|:-----------|:----------|:----------|
| RNF-01 | Procesar archivos ≤ 50 MB en < 60 segundos | Alta | Rendimiento |
| RNF-02 | Hashing de contraseñas con Werkzeug scrypt | Alta | Seguridad |
| RNF-03 | Cookies HttpOnly + SameSite=Lax | Alta | Seguridad |
| RNF-04 | Aislamiento de archivos por usuario (carpetas separadas) | Alta | Seguridad |
| RNF-05 | Soporte dual: threading (Windows) y eventlet (Linux) | Alta | Portabilidad |
| RNF-06 | Despliegue con Nginx + Gunicorn + Supervisor | Media | Operabilidad |
| RNF-07 | Errores del servidor devuelven JSON (no HTML) | Media | Interoperabilidad |

### 2.2. Restricciones

- El sistema está implementado en Python 3.12+ con Flask como framework web.
- El almacenamiento intermedio durante el ETL usa SQLite embebido.
- La autenticación usa SQLite local o MySQL (configurable por variable de entorno `MYSQL_DB`).
- El tamaño máximo de archivo es configurable (por defecto 500 MB).
- En Windows, SocketIO opera en modo threading; en Linux, en modo eventlet.

---

<span id="representacion-arquitectura"></span>
## 3. REPRESENTACIÓN DE LA ARQUITECTURA DEL SISTEMA

<span id="vista-caso-uso"></span>
### 3.1. Vista de Caso de uso

La vista de caso de uso describe los escenarios principales que la arquitectura debe soportar:

#### 3.1.1. Diagramas de Casos de uso

**Escenario principal: Migración de base de datos**

| Paso | Actor | Acción | Componente |
|:-----|:------|:-------|:-----------|
| 1 | Usuario | Inicia sesión (local u OAuth) | app/auth.py, app/oauth.py |
| 2 | Usuario | Sube archivo de base de datos | app/routes.py → POST /api/subir-archivo |
| 3 | Sistema | Detecta tipo de motor | utilidades/detector.py → DetectorBaseDatos.detectar() |
| 4 | Sistema | Extrae esquema y datos | extraccion/conector.py → ConectorOrigen |
| 5 | Usuario | Selecciona motor destino | Frontend JS → POST /api/iniciar-migracion |
| 6 | Sistema | Transforma datos | transformacion/mapeador.py → MapeadorDatos |
| 7 | Sistema | Carga en SQLite intermedio | carga/cargador.py → CargadorDestino |
| 8 | Sistema | Genera exportación nativa | carga/cargador.py → generar_export() |
| 9 | Usuario | Descarga resultado o sube a GitHub | app/routes.py → GET /api/descargar o POST /api/github/subir |

**Escenario: Administración de usuarios**

| Paso | Actor | Acción | Componente |
|:-----|:------|:-------|:-----------|
| 1 | Admin | Accede al panel de administración | app/routes.py → GET /admin |
| 2 | Admin | Crea nuevo administrador | app/auth.py → crear_nuevo_admin() |
| 3 | Admin | Elimina usuario | app/routes.py → POST /admin/eliminar |
| 4 | Sistema | Notifica al usuario eliminado por email | app/auth.py → enviar_email_notificacion() |

<span id="vista-logica"></span>
### 3.2. Vista Lógica

La vista lógica describe la estructura de clases y paquetes del sistema.

#### 3.2.1. Diagrama de Subsistemas (paquetes)

```
MigradorBD/
├── app/                        # Capa de Presentación + Autenticación
│   ├── __init__.py            # Factory de la aplicación Flask
│   ├── routes.py              # Blueprint principal (1453 líneas, todas las rutas)
│   ├── auth.py                # Sistema de autenticación (SQLite/MySQL)
│   ├── oauth.py               # Configuración OAuth (Google, GitHub)
│   ├── models.py              # Modelos de datos (dataclasses)
│   ├── github_integration.py  # Integración con GitHub API
│   ├── templates/             # Plantillas HTML (Jinja2)
│   └── static/                # CSS, JavaScript
├── extraccion/                 # Capa de Extracción (E del ETL)
│   ├── __init__.py
│   └── conector.py            # ConectorOrigen (561 líneas)
├── transformacion/             # Capa de Transformación (T del ETL)
│   ├── __init__.py
│   └── mapeador.py            # MapeadorDatos (39 líneas)
├── carga/                      # Capa de Carga (L del ETL)
│   ├── __init__.py
│   └── cargador.py            # CargadorDestino (505 líneas)
├── utilidades/                 # Utilidades del Sistema
│   ├── __init__.py
│   └── detector.py            # DetectorBaseDatos (211 líneas)
├── config/
│   └── configuracion.yaml     # Configuración general (YAML)
├── config.py                   # Configuración Flask (variables de entorno)
├── run.py                      # Punto de entrada desarrollo
├── wsgi.py                     # Punto de entrada producción (WSGI)
├── sql/
│   └── init_auth_db.sql       # Script de inicialización de BD auth
├── tests/                      # Pruebas del sistema
├── despliegue/                 # Scripts de despliegue
└── docs/                       # Documentación técnica
```

#### 3.2.2. Diagrama de Secuencia – Proceso de Migración

```
Usuario          routes.py        detector.py      conector.py      mapeador.py      cargador.py
  |                 |                 |                 |                 |                 |
  |-- POST /subir --|                 |                 |                 |                 |
  |                 |-- detectar() -->|                 |                 |                 |
  |                 |<-- (tipo,msg) --|                 |                 |                 |
  |                 |-- ConectorOrigen(ruta, tipo) ---->|                 |                 |
  |                 |<-- (tablas, esquema, datos) ------|                 |                 |
  |<-- JSON response|                 |                 |                 |                 |
  |                 |                 |                 |                 |                 |
  |-- POST /migrar -|                 |                 |                 |                 |
  |                 |-- CargadorDestino(motor_destino) ---------------------->|             |
  |                 |-- crear_estructura(esquema) --------------------------->|             |
  |                 |-- For each tabla:                 |                 |                 |
  |                 |   extraer_datos(tabla) ---------->|                 |                 |
  |                 |   limpiar_dataframe(df) ----------------------->|                    |
  |                 |   cargar_tabla(tabla, df) ------------------------------------------>|
  |                 |-- generar_export(motor) ----------------------------------------->|  |
  |                 |<-- (contenido, ext, mime) ---------------------------------------|  |
  |<-- JSON+archivo |                 |                 |                 |                 |
```

#### 3.2.3. Diagrama de Clases

**Clase: ConectorOrigen** (`extraccion/conector.py`)

| Atributo | Tipo | Descripción |
|:---------|:-----|:-----------|
| ruta | str | Ruta al archivo de base de datos |
| tipo | str | Tipo de motor detectado |
| engine | Engine | Motor SQLAlchemy (solo SQLite) |
| tablas | List[str] | Lista de tablas encontradas |
| esquema | Dict | Esquema de cada tabla (columnas, PKs, FKs, índices) |
| esquemas | Dict | Diccionario de esquemas: {nombre_esquema: [tablas]} |
| tabla_a_esquema | Dict | Mapeo: tabla → esquema |
| vistas | List[Dict] | Vistas SQL extraídas |
| triggers | List[Dict] | Triggers extraídos |
| procedimientos | List[Dict] | Procedimientos almacenados extraídos |
| funciones | List[Dict] | Funciones SQL extraídas |
| indices | List[Dict] | Índices SQL extraídos |

| Método | Retorno | Descripción |
|:-------|:--------|:-----------|
| _descubrir_sqlite() | None | Descubre esquema desde archivo SQLite |
| _analizar_sql() | None | Parsea scripts SQL con regex |
| _cargar_json() | None | Carga archivos JSON/NDJSON |
| _cargar_csv() | None | Carga archivos CSV |
| _cargar_excel() | None | Carga archivos Excel |
| _extraer_objetos_db(contenido) | None | Extrae vistas, triggers, procedimientos, funciones |
| extraer_datos(tabla) | DataFrame | Extrae datos de una tabla específica |

**Clase: MapeadorDatos** (`transformacion/mapeador.py`)

| Método | Retorno | Descripción |
|:-------|:--------|:-----------|
| limpiar_dataframe(df) | DataFrame | Normaliza nombres de columnas, convierte tipos, elimina nulos |
| preparar_para_destino(df, esquema_destino) | DataFrame | Adapta DataFrame al esquema destino |

**Clase: CargadorDestino** (`carga/cargador.py`)

| Atributo | Tipo | Descripción |
|:---------|:-----|:-----------|
| motor | str | Motor de destino |
| engine | Engine | Motor SQLAlchemy para SQLite intermedio |
| ruta_salida | str | Ruta al archivo SQLite intermedio |
| _tabla_export_map | Dict | Mapeo de tabla SQLite → (schema, table) |
| _stored_objs | Dict | Objetos SQL almacenados (vistas, triggers, etc.) |

| Método | Retorno | Descripción |
|:-------|:--------|:-----------|
| crear_estructura(esquema) | int | Crea tablas en SQLite intermedio |
| cargar_tabla(tabla, df) | int | Inserta datos en tabla SQLite |
| generar_export(motor) | tuple | Genera exportación (contenido, ext, mime, es_binario) |
| _generar_sql(motor) | str | Genera SQL nativo para el motor destino |
| _generar_json() | str | Genera JSON para MongoDB |
| _generar_ndjson() | str | Genera NDJSON para Elasticsearch |
| _generar_cql() | str | Genera CQL para Cassandra |
| _generar_redis() | str | Genera comandos Redis |

**Clase: DetectorBaseDatos** (`utilidades/detector.py`)

| Método | Retorno | Descripción |
|:-------|:--------|:-----------|
| detectar(ruta, nombre) | Tuple[str, str, Any] | Detecta tipo de BD desde contenido del archivo |

**Clase: ConfiguracionConexion** (`app/models.py`)

| Atributo | Tipo | Descripción |
|:---------|:-----|:-----------|
| motor | str | Motor de base de datos |
| host | str | Host del servidor |
| puerto | str | Puerto de conexión |
| usuario | str | Usuario de la base de datos |
| contrasena | str | Contraseña |
| nombre_bd | str | Nombre de la base de datos |

**Clase: EstadoMigracion** (`app/models.py`)

| Atributo | Tipo | Descripción |
|:---------|:-----|:-----------|
| proceso_id | str | Identificador del proceso |
| origen | ConfiguracionConexion | Configuración del origen |
| destino | ConfiguracionConexion | Configuración del destino |
| tablas_migrar | List[str] | Tablas pendientes |
| tablas_completadas | List[str] | Tablas migradas |
| metricas | Dict | Contadores: extraídos, cargados, errores, tablas_ok |

#### 3.2.4. Diagrama de Base de datos

El sistema utiliza dos bases de datos SQLite:

**1. Base de datos de autenticación** (`auth.db`):
- Tabla `usuarios`: Almacena credenciales y perfiles.
- Tabla `oauth_usuarios`: Almacena vinculaciones OAuth.
- Relación: `oauth_usuarios.usuario_id → usuarios.id` (FK).

**2. Base de datos intermedia ETL** (`uploads/migracion_<motor>.db`):
- Tablas dinámicas creadas durante el proceso de migración.
- Estructura refleja el esquema del archivo de origen con nombres normalizados.
- Se usa como almacenamiento temporal antes de generar la exportación final.

<span id="vista-implementacion"></span>
### 3.3. Vista de Implementación (vista de desarrollo)

#### 3.3.1. Diagrama de arquitectura software (paquetes)

La arquitectura se organiza en capas:

```
┌─────────────────────────────────────────────────┐
│                 CAPA DE PRESENTACIÓN             │
│  app/templates/ (HTML+Jinja2)                    │
│  app/static/css/ + app/static/js/                │
│  Flask-SocketIO (comunicación en tiempo real)    │
└──────────────────────┬──────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────┐
│                 CAPA DE APLICACIÓN               │
│  app/routes.py (Blueprint principal)             │
│  app/auth.py (Autenticación y autorización)      │
│  app/oauth.py (OAuth Google + GitHub)            │
│  app/github_integration.py (GitHub API)          │
│  app/models.py (Modelos de datos)                │
│  config.py (Configuración Flask)                 │
└──────────────────────┬──────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────┐
│                CAPA DE LÓGICA DE NEGOCIO (ETL)   │
│  ┌──────────┐  ┌──────────────┐  ┌───────────┐  │
│  │Extracción│→│Transformación│→│   Carga   │  │
│  │conector  │  │  mapeador    │  │ cargador  │  │
│  └──────────┘  └──────────────┘  └───────────┘  │
│  utilidades/detector.py (Detección automática)   │
└──────────────────────┬──────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────┐
│                 CAPA DE DATOS                    │
│  SQLite (auth.db - autenticación)                │
│  SQLite (migracion_<motor>.db - ETL intermedio)  │
│  SQLAlchemy (ORM para acceso a datos)            │
│  Pandas (manipulación de DataFrames)             │
└─────────────────────────────────────────────────┘
```

#### 3.3.2. Diagrama de componentes

```
┌─────────────────────────────────────────────────────────┐
│                      Navegador Web                       │
│  ┌──────────┐  ┌─────────────┐  ┌──────────────────┐   │
│  │ HTML/CSS │  │ JavaScript  │  │ Socket.IO Client │   │
│  └──────────┘  └─────────────┘  └──────────────────┘   │
└──────────────────────┬──────────────────────────────────┘
                       │ HTTP / WebSocket
┌──────────────────────▼──────────────────────────────────┐
│                   Servidor Flask                         │
│  ┌─────────────┐  ┌─────────────┐  ┌────────────────┐  │
│  │   Routes    │  │    Auth     │  │     OAuth      │  │
│  │ (Blueprint) │  │  (SQLite/  │  │ (Google/GitHub)│  │
│  │             │  │   MySQL)   │  │   (Authlib)    │  │
│  └──────┬──────┘  └─────────────┘  └────────────────┘  │
│         │                                                │
│  ┌──────▼──────────────────────────────────────────┐    │
│  │              Pipeline ETL                        │    │
│  │  ┌──────────┐  ┌────────────┐  ┌─────────────┐ │    │
│  │  │Detector  │→│ConectorOrig│→│MapeadorDatos│ │    │
│  │  │BaseDatos │  │   en       │  │             │ │    │
│  │  └──────────┘  └────────────┘  └──────┬──────┘ │    │
│  │                                        │        │    │
│  │                               ┌────────▼──────┐ │    │
│  │                               │CargadorDestino│ │    │
│  │                               │ (.sql/.json/  │ │    │
│  │                               │  .ndjson/.cql/│ │    │
│  │                               │  .redis/.db)  │ │    │
│  │                               └───────────────┘ │    │
│  └─────────────────────────────────────────────────┘    │
└──────────────────────┬──────────────────────────────────┘
                       │
         ┌─────────────┼──────────────┐
         │             │              │
    ┌────▼────┐  ┌─────▼─────┐  ┌────▼────┐
    │ SQLite  │  │ GitHub API│  │  SMTP   │
    │(auth.db)│  │(repos,    │  │(email   │
    │         │  │ archivos) │  │verific.)│
    └─────────┘  └───────────┘  └─────────┘
```

<span id="vista-procesos"></span>
### 3.4. Vista de procesos

#### 3.4.1. Diagrama de Procesos del sistema

**Proceso 1: Detección automática de motor** (`utilidades/detector.py`)

```
Archivo subido
      │
      ▼
┌─────────────┐    Sí    ┌──────────────┐
│ ¿Es SQLite? │────────→│ Return SQLite │
│(binary test)│          └──────────────┘
└──────┬──────┘
       │ No
       ▼
┌─────────────────┐   Sí   ┌───────────────────────┐
│¿Contiene CREATE │───────→│Analizar sintaxis SQL: │
│TABLE o INSERT?  │        │AUTO_INCREMENT → MySQL  │
└──────┬──────────┘        │SERIAL → PostgreSQL    │
       │ No                │IDENTITY → SQL Server  │
       ▼                   │VARCHAR2 → Oracle      │
┌─────────────────┐        │INT64 → BigQuery       │
│¿Es JSON válido? │        │VARIANT → Snowflake    │
│(array/object)   │        │DISTKEY → Redshift     │
└──────┬──────────┘        └───────────────────────┘
       │ No
       ▼
┌─────────────────┐
│¿Es CSV/Excel?   │
│(Pandas attempt)  │
└──────┬──────────┘
       │ No
       ▼
┌─────────────────┐
│Fallback:        │
│extensión archivo│
└─────────────────┘
```

**Proceso 2: Pipeline ETL**

```
1. EXTRACCIÓN (ConectorOrigen)
   ├── SQLite: SQLAlchemy inspect → tablas, columnas, PKs, FKs, índices
   ├── SQL: Regex parsing → CREATE TABLE, INSERT INTO, CREATE VIEW/TRIGGER/PROC/FUNC
   ├── JSON: json.load → documentos
   ├── CSV: Pandas read_csv → DataFrame
   └── Excel: Pandas read_excel → DataFrame por hoja

2. TRANSFORMACIÓN (MapeadorDatos)
   ├── Normalizar nombres de columnas (espacios→_, guiones→_, puntos→_)
   ├── Convertir tipos object → string
   └── Eliminar filas completamente nulas

3. CARGA (CargadorDestino)
   ├── Crear SQLite intermedio
   ├── Crear tablas con estructura traducida
   ├── Insertar datos vía Pandas to_sql
   ├── Almacenar objetos SQL (vistas, triggers, etc.)
   └── Generar exportación final según motor:
       ├── SQL: CREATE TABLE + INSERT INTO con tipos nativos
       ├── JSON: metadata + collections
       ├── NDJSON: índice + documento por línea
       ├── CQL: CREATE TABLE + INSERT con PRIMARY KEY
       └── Redis: HSET por fila
```

<span id="vista-despliegue"></span>
### 3.5. Vista de Despliegue (vista física)

#### 3.5.1. Diagrama de despliegue

**Entorno de Desarrollo (Local)**:

```
┌──────────────────────────────┐
│      Equipo del Desarrollador │
│  ┌────────────────────────┐  │
│  │    Python 3.12+        │  │
│  │    Flask (run.py)      │  │
│  │    Puerto: 5000        │  │
│  │    Modo: threading     │  │
│  └────────────────────────┘  │
│  ┌────────────────────────┐  │
│  │    SQLite (auth.db)    │  │
│  │    uploads/            │  │
│  └────────────────────────┘  │
└──────────────────────────────┘
```

**Entorno de Producción (VPS Ubuntu)**:

```
┌─────────────────────────────────────────────────────┐
│                    VPS Ubuntu 22.04                   │
│                                                       │
│  ┌─────────────────────┐    ┌──────────────────────┐ │
│  │      Nginx          │    │    Supervisor         │ │
│  │  Puerto: 80/443     │    │  (gestión procesos)   │ │
│  │  SSL: Let's Encrypt │    └──────────┬───────────┘ │
│  │  Proxy → :5000      │               │             │
│  └──────────┬──────────┘    ┌──────────▼───────────┐ │
│             │               │ Gunicorn + Eventlet  │ │
│             └──────────────→│ wsgi.py              │ │
│                             │ Workers: 1 (eventlet)│ │
│                             │ Puerto: 5000         │ │
│                             └──────────────────────┘ │
│                                                       │
│  ┌──────────────────┐    ┌──────────────────────┐    │
│  │  SQLite auth.db  │    │  uploads/ (archivos) │    │
│  └──────────────────┘    └──────────────────────┘    │
│                                                       │
│  ── Servicios Externos ──                             │
│  ├── Google OAuth (accounts.google.com)               │
│  ├── GitHub OAuth (github.com/login/oauth)            │
│  ├── GitHub API (api.github.com)                      │
│  └── SMTP (smtp.gmail.com:587)                        │
└───────────────────────────────────────────────────────┘
```

---

<span id="atributos-calidad"></span>
## 4. ATRIBUTOS DE CALIDAD DEL SOFTWARE

### Escenario de Funcionalidad

| Atributo | Descripción | Métrica |
|:---------|:-----------|:--------|
| Completitud | El sistema soporta migración entre 15+ motores de BD | Motores soportados: MySQL, PostgreSQL, SQL Server, Oracle, SQLite, MongoDB, Elasticsearch, Cassandra, Redis, Snowflake, BigQuery, Redshift, MariaDB, Db2, Azure SQL |
| Correctitud | Los datos migrados son idénticos a los datos originales | Ratio registros_cargados / registros_extraídos = 100% |
| Detección | El sistema identifica correctamente el motor de origen | Tasa de detección correcta > 95% (validado con test_deteccion_bd.py) |

### Escenario de Usabilidad

| Atributo | Descripción | Métrica |
|:---------|:-----------|:--------|
| Facilidad de aprendizaje | Un usuario nuevo puede completar su primera migración sin documentación | Tiempo < 5 minutos |
| Pasos del proceso | El flujo de migración requiere mínimos pasos | 4 pasos: subir → seleccionar destino → migrar → descargar |
| Feedback visual | El sistema muestra progreso en tiempo real | Actualizaciones vía WebSocket cada tabla procesada |

### Escenario de confiabilidad

| Atributo | Descripción | Métrica |
|:---------|:-----------|:--------|
| Tolerancia a errores | El sistema maneja archivos malformados sin caerse | Excepciones capturadas con respuestas JSON de error |
| Disponibilidad | El servicio web está disponible continuamente | Uptime > 99% con Supervisor para reinicio automático |
| Integridad de datos | Los datos no se pierden ni corrompen durante la migración | Validación de métricas: extraídos == cargados |

### Escenario de rendimiento

| Atributo | Descripción | Métrica |
|:---------|:-----------|:--------|
| Tiempo de respuesta | Detección de motor en archivo de 2 MB | < 1 segundo |
| Throughput | Migración completa de archivo de 50 MB | < 60 segundos |
| Uso de memoria | Procesamiento con Pandas DataFrame | Proporcional al tamaño del archivo |

### Escenario de mantenibilidad

| Atributo | Descripción | Métrica |
|:---------|:-----------|:--------|
| Modularidad | Pipeline ETL separado en 3 módulos independientes | Cada módulo puede modificarse sin afectar los demás |
| Extensibilidad | Agregar soporte para un nuevo motor | Requiere modificar solo CargadorDestino._generar_sql() |
| Documentación | Código documentado con docstrings | Todas las clases y funciones principales tienen docstrings |

### Otros Escenarios

**Portabilidad**: El sistema funciona tanto en Windows como en Linux gracias a la detección automática del modo asíncrono de SocketIO (`threading` en Windows, `eventlet` en Linux). La configuración de producción incluye scripts para Ubuntu (`deploy_ubuntu.sh`, `setup_produccion.sh`) y Windows (`push_vps.ps1`).

**Seguridad**: 
- Contraseñas hasheadas con Werkzeug scrypt.
- Cookies de sesión con HttpOnly, SameSite=Lax.
- Aislamiento de archivos por usuario (carpetas separadas en uploads/).
- OAuth 2.0 con Google y GitHub.
- Middleware ProxyFix para operación detrás de Nginx.
- Manejador global de errores que devuelve JSON (no HTML con información sensible).
