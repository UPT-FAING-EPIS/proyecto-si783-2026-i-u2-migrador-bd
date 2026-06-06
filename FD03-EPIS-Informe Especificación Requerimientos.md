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

Documento de Especificación de Requerimientos de Software

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

**INDICE GENERAL**

#  {#section .TOC-Heading}

[INTRODUCCION](#introduccion) 

[I. Generalidades del Proyecto](#generalidades-del-proyecto)

[1. Nombre del Proyecto](#nombre-del-proyecto)

[2. Visión](#vision-del-proyecto)

[3. Misión](#mision-del-proyecto)

[4. Organigrama](#organigrama)

[II. Visionamiento del Proyecto](#visionamiento-del-proyecto)

[1. Descripción del Problema](#descripcion-del-problema)

[2. Objetivos de Negocios](#objetivos-de-negocios)

[3. Objetivos de Diseño](#objetivos-de-diseno)

[4. Alcance del proyecto](#alcance-del-proyecto)

[5. Viabilidad del Sistema](#viabilidad-del-sistema)

[6. Información obtenida del Levantamiento de Información](#informacion-obtenida)

[III. Análisis de Procesos](#analisis-de-procesos)

[a) Diagrama del Proceso Actual](#proceso-actual)

[b) Diagrama del Proceso Propuesto](#proceso-propuesto)

[IV. Especificación de Requerimientos de Software](#especificacion-requerimientos)

[a) Cuadro de Requerimientos funcionales](#requerimientos-funcionales)

[b) Cuadro de Requerimientos No funcionales](#requerimientos-no-funcionales)

[c) Reglas de Negocio](#reglas-de-negocio)

[V. Fase de Desarrollo](#fase-de-desarrollo)

[1. Perfiles de Usuario](#perfiles-de-usuario)

[2. Modelo Conceptual](#modelo-conceptual)

[CONCLUSIONES](#conclusiones-srs)

[RECOMENDACIONES](#recomendaciones-srs)

[BIBLIOGRAFIA](#bibliografia-srs)

[WEBGRAFIA](#webgrafia-srs)

---

<span id="introduccion"></span>
## INTRODUCCION

El presente documento detalla la Especificación de Requerimientos de Software (SRS) para el sistema MigradorBD, una aplicación web integral de migración de bases de datos. Este documento describe los requerimientos funcionales y no funcionales del sistema, los perfiles de usuario, los procesos involucrados y las reglas de negocio que rigen su funcionamiento.

MigradorBD fue concebido para resolver la problemática de la migración de datos entre sistemas de gestión de bases de datos heterogéneos, proporcionando una solución automatizada basada en el paradigma ETL (Extracción, Transformación y Carga).

---

<span id="generalidades-del-proyecto"></span>
## I. Generalidades del Proyecto

<span id="nombre-del-proyecto"></span>
### 1. Nombre del Proyecto

MigradorBD – Sistema Integral de Migración de Bases de Datos

<span id="vision-del-proyecto"></span>
### 2. Visión

Ser la herramienta de referencia en migración multi-motor de bases de datos de código abierto, democratizando el acceso a procesos ETL automatizados para desarrolladores, administradores de bases de datos y organizaciones de todos los tamaños.

<span id="mision-del-proyecto"></span>
### 3. Misión

Facilitar la migración segura, eficiente y precisa de datos entre más de 15 motores de bases de datos mediante una interfaz web intuitiva, detección automática de motores y generación de exportaciones nativas para cada plataforma.

<span id="organigrama"></span>
### 4. Organigrama

| Rol | Integrante | Responsabilidades |
|:----|:-----------|:------------------|
| Desarrollador Backend / ETL | LLica Mamani, Jimmy Mijair | Módulos de extracción, transformación, carga, detección automática, tests |
| Desarrollador Frontend / Auth | Halanocca Rojas, Usher Damiron | Interfaz web, autenticación, OAuth, integración GitHub, plantillas HTML |

---

<span id="visionamiento-del-proyecto"></span>
## II. Visionamiento del Proyecto

<span id="descripcion-del-problema"></span>
### 1. Descripción del Problema

Las organizaciones enfrentan constantemente la necesidad de migrar datos entre diferentes motores de bases de datos. Este proceso, realizado manualmente, presenta múltiples desafíos:

- Cada motor tiene su propia sintaxis SQL, tipos de datos y características.
- Las herramientas comerciales son costosas y generalmente soportan solo 2-3 motores.
- Los procesos manuales son lentos, propensos a errores y difíciles de reproducir.
- No existe detección automática del tipo de archivo en la mayoría de herramientas.

<span id="objetivos-de-negocios"></span>
### 2. Objetivos de Negocios

- Reducir el tiempo de migración de días a minutos.
- Eliminar la dependencia de herramientas comerciales costosas.
- Proporcionar una solución multi-motor unificada.
- Minimizar errores en el proceso de migración.

<span id="objetivos-de-diseno"></span>
### 3. Objetivos de Diseño

- Arquitectura modular ETL (extracción → transformación → carga).
- Interfaz web responsiva con actualizaciones en tiempo real.
- Detección automática basada en análisis de contenido (no solo extensión).
- Autenticación segura multi-proveedor.
- Aislamiento de datos por usuario.

<span id="alcance-del-proyecto"></span>
### 4. Alcance del proyecto

El sistema abarca:

- **Formatos de entrada**: SQLite (.db, .sqlite), SQL (.sql, .dump), JSON (.json), NDJSON (.ndjson), CSV (.csv), Excel (.xlsx, .xls), CQL (.cql).
- **Motores destino**: MySQL, PostgreSQL, Microsoft SQL Server, Oracle, SQLite, MongoDB, Elasticsearch, Apache Cassandra, Redis, Snowflake, Google BigQuery, Amazon Redshift, MariaDB, IBM Db2, Azure SQL.
- **Funcionalidades**: Autenticación, migración ETL, historial, administración, integración GitHub.

No incluye:
- Conexión directa a servidores de bases de datos remotos.
- Migración incremental o en tiempo real.
- Soporte para archivos .bak binarios (requiere restauración previa).

<span id="viabilidad-del-sistema"></span>
### 5. Viabilidad del Sistema

El sistema ha sido validado como viable técnica, económica y operativamente según el Informe de Factibilidad (FD01).

<span id="informacion-obtenida"></span>
### 6. Información obtenida del Levantamiento de Información

- Se analizaron las funcionalidades de herramientas existentes: AWS DMS, Azure Database Migration, MySQL Workbench, pgAdmin, DBeaver.
- Se identificaron las limitaciones: costo, soporte limitado de motores, falta de detección automática.
- Se recopilaron patrones sintácticos de SQL para cada motor para implementar la detección automática.

---

<span id="analisis-de-procesos"></span>
## III. Análisis de Procesos

<span id="proceso-actual"></span>
### a) Diagrama del Proceso Actual – Diagrama de actividades

Proceso manual actual de migración:

1. El DBA identifica manualmente el tipo de base de datos de origen.
2. Exporta los datos usando la herramienta nativa del motor de origen.
3. Analiza las diferencias de tipos de datos entre origen y destino.
4. Escribe scripts manuales de transformación.
5. Ejecuta los scripts de creación de tablas en el motor destino.
6. Importa los datos manualmente.
7. Verifica la integridad de los datos migrados.

**Problemas identificados**: Proceso largo (2-5 días), propenso a errores, requiere conocimiento especializado de ambos motores, no es reproducible.

<span id="proceso-propuesto"></span>
### b) Diagrama del Proceso Propuesto – Diagrama de actividades

Proceso automatizado con MigradorBD:

1. El usuario inicia sesión en la aplicación web.
2. Sube el archivo de base de datos de origen.
3. El sistema detecta automáticamente el motor de origen (DetectorBaseDatos).
4. El sistema extrae el esquema y los datos (ConectorOrigen).
5. El usuario selecciona el motor de destino.
6. El sistema transforma los datos (MapeadorDatos).
7. El sistema genera la exportación nativa (CargadorDestino).
8. El usuario descarga el resultado o lo sube a GitHub.

**Mejoras**: Proceso completo en minutos, detección automática, transformación sin intervención humana, múltiples formatos de exportación.

---

<span id="especificacion-requerimientos"></span>
## IV. Especificación de Requerimientos de Software

<span id="requerimientos-funcionales"></span>
### a) Cuadro de Requerimientos Funcionales

| ID | Descripción | Prioridad | Módulo |
|:---|:-----------|:----------|:-------|
| RF-01 | El sistema debe permitir subir archivos de base de datos (hasta 500 MB) | Alta | app/routes.py |
| RF-02 | El sistema debe detectar automáticamente el tipo de motor de la base de datos de origen | Alta | utilidades/detector.py |
| RF-03 | El sistema debe extraer el esquema completo (tablas, columnas, claves, índices) del archivo de origen | Alta | extraccion/conector.py |
| RF-04 | El sistema debe extraer los datos de cada tabla del archivo de origen | Alta | extraccion/conector.py |
| RF-05 | El sistema debe transformar los datos para compatibilidad con el motor destino | Alta | transformacion/mapeador.py |
| RF-06 | El sistema debe generar exportaciones SQL nativas para cada motor destino | Alta | carga/cargador.py |
| RF-07 | El sistema debe generar exportaciones JSON para MongoDB | Media | carga/cargador.py |
| RF-08 | El sistema debe generar exportaciones NDJSON para Elasticsearch | Media | carga/cargador.py |
| RF-09 | El sistema debe generar exportaciones CQL para Apache Cassandra | Media | carga/cargador.py |
| RF-10 | El sistema debe generar comandos Redis (HSET) | Media | carga/cargador.py |
| RF-11 | El sistema debe permitir registro de usuarios con verificación por email | Alta | app/auth.py |
| RF-12 | El sistema debe permitir login con credenciales locales | Alta | app/auth.py |
| RF-13 | El sistema debe permitir login con Google OAuth | Media | app/oauth.py |
| RF-14 | El sistema debe permitir login con GitHub OAuth | Media | app/oauth.py |
| RF-15 | El sistema debe permitir descargar el archivo migrado | Alta | app/routes.py |
| RF-16 | El sistema debe permitir subir archivos migrados a GitHub | Baja | app/routes.py |
| RF-17 | El sistema debe listar los repositorios GitHub del usuario | Baja | app/routes.py |
| RF-18 | El sistema debe permitir crear repositorios GitHub desde la interfaz | Baja | app/routes.py |
| RF-19 | El sistema debe mostrar el historial de migraciones realizadas | Media | app/routes.py |
| RF-20 | El sistema debe permitir la administración de usuarios (crear admin, eliminar usuario) | Media | app/auth.py |
| RF-21 | El sistema debe registrar y mostrar accesos por IP | Baja | app/routes.py |
| RF-22 | El sistema debe preservar vistas, triggers, procedimientos y funciones del origen | Media | extraccion/conector.py, carga/cargador.py |
| RF-23 | El sistema debe notificar el progreso de migración en tiempo real vía WebSocket | Media | app/routes.py |
| RF-24 | El sistema debe permitir la gestión del perfil de usuario (foto, descripción) | Baja | app/auth.py |

<span id="requerimientos-no-funcionales"></span>
### b) Cuadro de Requerimientos No Funcionales

| ID | Descripción | Prioridad | Categoría |
|:---|:-----------|:----------|:----------|
| RNF-01 | El sistema debe procesar archivos de hasta 50 MB en menos de 60 segundos | Alta | Rendimiento |
| RNF-02 | Las contraseñas deben almacenarse con hash scrypt (Werkzeug) | Alta | Seguridad |
| RNF-03 | Las cookies de sesión deben ser HttpOnly y SameSite=Lax | Alta | Seguridad |
| RNF-04 | El sistema debe soportar al menos 10 usuarios concurrentes | Media | Escalabilidad |
| RNF-05 | La interfaz debe ser responsive y compatible con navegadores modernos | Media | Usabilidad |
| RNF-06 | El sistema debe aislar los archivos de cada usuario en carpetas separadas | Alta | Seguridad |
| RNF-07 | Los errores del servidor deben devolver JSON, no HTML | Media | Mantenibilidad |
| RNF-08 | El sistema debe soportar despliegue con Nginx + Gunicorn + Supervisor | Media | Portabilidad |
| RNF-09 | El tamaño máximo de archivo debe ser configurable | Baja | Configurabilidad |
| RNF-10 | El sistema debe funcionar tanto en Windows (threading) como en Linux (eventlet) | Alta | Portabilidad |

<span id="reglas-de-negocio"></span>
### c) Reglas de Negocio

| ID | Regla | Descripción |
|:---|:------|:-----------|
| RN-01 | Autenticación obligatoria | Todas las rutas de migración requieren autenticación previa |
| RN-02 | Verificación de email | Los usuarios registrados localmente deben verificar su email con un código de 6 dígitos antes de poder iniciar sesión |
| RN-03 | Roles de usuario | Existen dos roles: 'usuario' (acceso a migración) y 'admin' (acceso a migración + administración + monitoreo IP) |
| RN-04 | Admin por defecto | El sistema crea un administrador por defecto (admin/admin123) si no existe ninguno |
| RN-05 | Notificación por eliminación | Cuando un admin elimina un usuario, se envía notificación por email al usuario eliminado |
| RN-06 | Detección sobre extensión | El sistema prioriza la detección por contenido sobre la extensión del archivo |
| RN-07 | Esquema público por defecto | Si no se detecta un esquema explícito en el SQL, se asigna 'public' como esquema por defecto |
| RN-08 | Límite de IPs | El sistema registra un máximo de 1000 IPs para evitar crecimiento ilimitado de memoria |

---

<span id="fase-de-desarrollo"></span>
## V. Fase de Desarrollo

<span id="perfiles-de-usuario"></span>
### 1. Perfiles de Usuario

| Perfil | Descripción | Permisos |
|:-------|:-----------|:---------|
| Usuario regular | Puede subir archivos, ejecutar migraciones, descargar resultados, ver historial, gestionar perfil, conectar GitHub | Acceso a rutas de migración y perfil |
| Administrador | Todas las funciones de usuario regular + gestión de usuarios + monitoreo de IPs + creación de admins | Acceso completo al sistema |

<span id="modelo-conceptual"></span>
### 2. Modelo Conceptual

#### a) Diagrama de Paquetes

El sistema está organizado en los siguientes paquetes/módulos:

- **app/**: Aplicación Flask principal (rutas, templates, static, auth, oauth, models)
- **extraccion/**: Módulo de extracción de datos (ConectorOrigen)
- **transformacion/**: Módulo de transformación (MapeadorDatos)
- **carga/**: Módulo de carga (CargadorDestino)
- **utilidades/**: Utilidades del sistema (DetectorBaseDatos)
- **config/**: Configuración del sistema (YAML)
- **tests/**: Pruebas del sistema
- **despliegue/**: Scripts de despliegue en producción
- **docs/**: Documentación técnica

#### b) Diagrama de Casos de Uso

**Actores:**
- Usuario regular
- Administrador
- Sistema externo (Google OAuth, GitHub OAuth, GitHub API, SMTP)

**Casos de uso principales:**

| CU-ID | Caso de Uso | Actor | Descripción |
|:------|:-----------|:------|:-----------|
| CU-01 | Registrar cuenta | Usuario | El usuario se registra con nombre, email y contraseña |
| CU-02 | Verificar email | Usuario/Sistema | El sistema envía código de 6 dígitos por email; el usuario lo ingresa para activar cuenta |
| CU-03 | Iniciar sesión | Usuario | El usuario ingresa credenciales para acceder al sistema |
| CU-04 | Login OAuth | Usuario/Sistema externo | El usuario se autentica vía Google o GitHub |
| CU-05 | Subir archivo BD | Usuario | El usuario sube un archivo de base de datos |
| CU-06 | Detectar motor | Sistema | El sistema analiza el contenido y detecta el tipo de motor |
| CU-07 | Seleccionar destino | Usuario | El usuario elige el motor de base de datos destino |
| CU-08 | Ejecutar migración | Sistema | El sistema ejecuta el proceso ETL completo |
| CU-09 | Descargar resultado | Usuario | El usuario descarga el archivo migrado |
| CU-10 | Subir a GitHub | Usuario | El usuario sube el resultado a un repositorio GitHub |
| CU-11 | Ver historial | Usuario | El usuario consulta el historial de migraciones |
| CU-12 | Gestionar usuarios | Administrador | El admin crea/elimina usuarios y asigna roles |
| CU-13 | Monitorear IPs | Administrador | El admin revisa los accesos por IP al sistema |
| CU-14 | Gestionar perfil | Usuario | El usuario actualiza su foto y descripción |

#### c) Modelo de datos

**Tabla: usuarios**

| Columna | Tipo | Restricciones | Descripción |
|:--------|:-----|:-------------|:-----------|
| id | INTEGER | PK, AUTOINCREMENT | Identificador único |
| usuario | TEXT | UNIQUE, NOT NULL | Nombre de usuario |
| email | TEXT | UNIQUE, NOT NULL | Correo electrónico |
| contraseña | TEXT | | Hash de la contraseña (scrypt) |
| rol | TEXT | NOT NULL, DEFAULT 'usuario' | Rol del usuario (usuario/admin) |
| creado_en | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | Fecha de creación |
| activo | BOOLEAN | DEFAULT 1 | Estado de la cuenta |
| verification_code | TEXT | | Código de verificación de 6 dígitos |
| verified | BOOLEAN | DEFAULT 0 | Estado de verificación de email |
| foto_perfil | TEXT | | Foto de perfil en Base64 |
| descripcion | TEXT | | Descripción del perfil |

**Tabla: oauth_usuarios**

| Columna | Tipo | Restricciones | Descripción |
|:--------|:-----|:-------------|:-----------|
| id | INTEGER | PK, AUTOINCREMENT | Identificador único |
| usuario_id | INTEGER | FK → usuarios(id), NOT NULL | Relación con tabla usuarios |
| proveedor | TEXT | NOT NULL | Proveedor OAuth (google/github) |
| proveedor_id | TEXT | NOT NULL | ID del usuario en el proveedor |
| email | TEXT | NOT NULL | Email del proveedor |
| nombre | TEXT | | Nombre del proveedor |
| foto_url | TEXT | | URL de foto del proveedor |
| creado_en | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | Fecha de vinculación |

---

<span id="conclusiones-srs"></span>
## CONCLUSIONES

El documento SRS define de manera integral los requerimientos funcionales y no funcionales del sistema MigradorBD. Se han identificado 24 requerimientos funcionales y 10 no funcionales que cubren desde la funcionalidad core (proceso ETL) hasta aspectos de seguridad, usabilidad y portabilidad. El sistema está diseñado con una arquitectura modular que facilita su extensión y mantenimiento.

<span id="recomendaciones-srs"></span>
## RECOMENDACIONES

- Priorizar la implementación de los requerimientos críticos (RF-01 a RF-06) antes de las funcionalidades complementarias.
- Implementar pruebas automatizadas para cada requerimiento funcional.
- Documentar las APIs REST del sistema para facilitar la integración con otros sistemas.
- Considerar la implementación de un sistema de caché para mejorar el rendimiento con archivos grandes.

<span id="bibliografia-srs"></span>
## BIBLIOGRAFIA

- IEEE Std 830-1998: IEEE Recommended Practice for Software Requirements Specifications.
- Sommerville, I. (2016). *Software Engineering* (10ª ed.). Pearson.
- Pressman, R. S. (2014). *Ingeniería del Software: Un Enfoque Práctico* (8ª ed.). McGraw-Hill.

<span id="webgrafia-srs"></span>
## WEBGRAFIA

- Flask Documentation: https://flask.palletsprojects.com/
- SQLAlchemy Documentation: https://docs.sqlalchemy.org/
- Authlib Documentation: https://docs.authlib.org/
- Flask-SocketIO Documentation: https://flask-socketio.readthedocs.io/
