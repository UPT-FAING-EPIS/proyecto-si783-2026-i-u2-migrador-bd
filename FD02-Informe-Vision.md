<center>

[comment]: <img src="./media/media/image1.png" style="width:1.088in;height:1.46256in" alt="escudo.png" />

![./media/media/image1.png](./media/logo-upt.png)

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

**  
**
</center>
<div style="page-break-after: always; visibility: hidden">\pagebreak</div>

|CONTROL DE VERSIONES||||||
| :-: | :- | :- | :- | :- | :- |
|Versión|Hecha por|Revisada por|Aprobada por|Fecha|Motivo|
|1\.0|JLM / UHR|JLM|UHR|06/06/2026|Versión Original|

**Sistema *MigradorBD***

**Documento de Visión**

**Versión *1.0***

<div style="page-break-after: always; visibility: hidden">\pagebreak</div>

|CONTROL DE VERSIONES||||||
| :-: | :- | :- | :- | :- | :- |
|Versión|Hecha por|Revisada por|Aprobada por|Fecha|Motivo|
|1\.0|JLM / UHR|JLM|UHR|06/06/2026|Versión Original|


<div style="page-break-after: always; visibility: hidden">\pagebreak</div>


**INDICE GENERAL**
#
[1.	Introducción](#_Toc52661346)

1.1	Propósito

1.2	Alcance

1.3	Definiciones, Siglas y Abreviaturas

1.4	Referencias

1.5	Visión General

[2.	Posicionamiento](#_Toc52661347)

2.1	Oportunidad de negocio

2.2	Definición del problema

[3.	Descripción de los interesados y usuarios](#_Toc52661348)

3.1	Resumen de los interesados

3.2	Resumen de los usuarios

3.3	Entorno de usuario

3.4	Perfiles de los interesados

3.5	Perfiles de los Usuarios

3.6	Necesidades de los interesados y usuarios

[4.	Vista General del Producto](#_Toc52661349)

4.1	Perspectiva del producto

4.2	Resumen de capacidades

4.3	Suposiciones y dependencias

4.4	Costos y precios

4.5	Licenciamiento e instalación

[5.	Características del producto](#_Toc52661350)

[6.	Restricciones](#_Toc52661351)

[7.	Rangos de calidad](#_Toc52661352)

[8.	Precedencia y Prioridad](#_Toc52661353)

[9.	Otros requerimientos del producto](#_Toc52661354)

[CONCLUSIONES](#_Toc52661355)

[RECOMENDACIONES](#_Toc52661356)

[BIBLIOGRAFIA](#_Toc52661357)

[WEBGRAFIA](#_Toc52661358)


<div style="page-break-after: always; visibility: hidden">\pagebreak</div>

**<u>Informe de Visión</u>**

1. <span id="_Toc52661346" class="anchor"></span>**Introducción**

    1.1	Propósito

    El propósito de este documento es definir la visión del sistema MigradorBD, describiendo sus características, alcance y los objetivos que se pretenden alcanzar. Este documento está dirigido a los integrantes del equipo de desarrollo, al docente evaluador y a cualquier interesado en comprender la dirección y los beneficios del proyecto.

    1.2	Alcance

    MigradorBD es un sistema web de migración de bases de datos que implementa un proceso ETL (Extracción, Transformación y Carga) completo. El sistema permite:
    
    - Subir archivos de bases de datos en múltiples formatos (SQLite, SQL, JSON, CSV, Excel).
    - Detectar automáticamente el tipo y motor de la base de datos de origen.
    - Migrar datos hacia más de 15 motores destino (MySQL, PostgreSQL, SQL Server, Oracle, MongoDB, Elasticsearch, Cassandra, Redis, Snowflake, BigQuery, Redshift, entre otros).
    - Preservar esquemas, vistas, triggers, procedimientos almacenados, funciones e índices durante la migración.
    - Integrar autenticación segura con OAuth (Google/GitHub) y verificación por email.
    - Almacenar y versionar exportaciones directamente en repositorios de GitHub.
    - Monitorear el progreso de migración en tiempo real mediante WebSocket.

    1.3	Definiciones, Siglas y Abreviaturas

    | Término | Definición |
    |:--------|:-----------|
    | ETL | Extracción, Transformación y Carga (Extract, Transform, Load) |
    | OAuth | Estándar abierto de autorización para acceso delegado |
    | WebSocket | Protocolo de comunicación bidireccional sobre TCP |
    | SGBD | Sistema de Gestión de Bases de Datos |
    | API | Interfaz de Programación de Aplicaciones |
    | REST | Transferencia de Estado Representacional |
    | SQL | Lenguaje de Consulta Estructurado |
    | NoSQL | Bases de datos no relacionales |
    | NDJSON | Newline-Delimited JSON |
    | CQL | Cassandra Query Language |
    | VPS | Servidor Privado Virtual |
    | WSGI | Web Server Gateway Interface |
    | ORM | Mapeo Objeto-Relacional |

    1.4	Referencias

    - Documentación oficial de Flask: https://flask.palletsprojects.com/
    - SQLAlchemy Documentation: https://docs.sqlalchemy.org/
    - Authlib Documentation: https://docs.authlib.org/
    - Flask-SocketIO Documentation: https://flask-socketio.readthedocs.io/
    - Pandas Documentation: https://pandas.pydata.org/docs/

    1.5	Visión General

    El documento describe el posicionamiento del producto MigradorBD en el mercado de herramientas de migración de datos, identifica a los interesados y usuarios del sistema, presenta las capacidades principales del producto y establece las restricciones y rangos de calidad esperados.

<div style="page-break-after: always; visibility: hidden">\pagebreak</div>

2. <span id="_Toc52661347" class="anchor"></span>**Posicionamiento**

    2.1	Oportunidad de negocio

    El mercado de migración de bases de datos está dominado por soluciones comerciales costosas (AWS DMS, Azure Database Migration Service, Oracle Data Pump) o herramientas específicas para pares de motores. Existe una oportunidad significativa para una herramienta gratuita, de código abierto, que soporte migración multi-motor desde una interfaz web unificada.

    MigradorBD llena este vacío ofreciendo:
    - Soporte para más de 15 motores de bases de datos (relacionales y NoSQL).
    - Detección automática del tipo de base de datos sin configuración manual.
    - Interfaz web accesible desde cualquier navegador sin instalación local.
    - Costo cero de licenciamiento al ser de código abierto.

    2.2	Definición del problema

    | Elemento | Descripción |
    |:---------|:-----------|
    | **El problema de** | Migrar datos entre motores de bases de datos heterogéneos |
    | **Afecta a** | Administradores de bases de datos, desarrolladores, empresas en proceso de modernización |
    | **El impacto es** | Procesos manuales largos (días/semanas), propensos a errores, costosos y que requieren conocimiento especializado de cada motor |
    | **Una solución exitosa** | Automatizaría el proceso ETL, detectaría automáticamente el motor de origen, traduciría esquemas y datos entre motores, y proporcionaría una interfaz web intuitiva para todo el proceso |

<div style="page-break-after: always; visibility: hidden">\pagebreak</div>

3. <span id="_Toc52661348" class="anchor"></span>**Descripción de los interesados y usuarios**

    3.1	Resumen de los interesados

    | Nombre | Descripción | Responsabilidad |
    |:-------|:-----------|:----------------|
    | Equipo de desarrollo | LLica Mamani, Jimmy Mijair y Halanocca Rojas, Usher Damiron | Diseño, desarrollo, pruebas y documentación del sistema |
    | Docente evaluador | Docente del curso SI783 | Evaluación y retroalimentación del proyecto |
    | Administradores de BD | Profesionales que gestionan bases de datos | Usuarios principales del sistema de migración |
    | Desarrolladores de software | Profesionales que necesitan migrar datos durante el desarrollo | Usuarios secundarios del sistema |

    3.2	Resumen de los usuarios

    | Nombre | Descripción | Interesado |
    |:-------|:-----------|:-----------|
    | Usuario regular | Persona que necesita migrar bases de datos entre formatos | Equipo de desarrollo |
    | Administrador | Usuario con privilegios para gestionar otros usuarios y monitorear IPs | Equipo de desarrollo |

    3.3	Entorno de usuario

    Los usuarios acceden al sistema a través de un navegador web moderno (Chrome, Firefox, Edge, Safari). No se requiere instalación de software adicional en el equipo del usuario. El sistema presenta una interfaz paso a paso que guía al usuario en el proceso de migración:
    
    1. **Autenticación**: Login con credenciales locales u OAuth (Google/GitHub).
    2. **Carga**: Subir el archivo de base de datos de origen.
    3. **Detección**: El sistema detecta automáticamente el motor de origen.
    4. **Selección**: El usuario selecciona el motor de destino.
    5. **Migración**: El sistema ejecuta el proceso ETL con progreso en tiempo real.
    6. **Descarga/GitHub**: El usuario descarga el archivo migrado o lo sube a GitHub.

    3.4	Perfiles de los interesados

    **Equipo de desarrollo:**
    - **Representantes**: LLica Mamani, Jimmy Mijair (Backend/ETL) y Halanocca Rojas, Usher Damiron (Frontend/Auth)
    - **Tipo**: Desarrolladores
    - **Responsabilidades**: Análisis, diseño, codificación, pruebas, despliegue y documentación
    - **Criterio de éxito**: Sistema funcional que migre datos correctamente entre al menos 10 motores distintos

    3.5	Perfiles de los Usuarios

    **Usuario regular:**
    - **Representante**: Cualquier profesional de TI
    - **Descripción**: Persona con conocimientos básicos de bases de datos que necesita migrar datos
    - **Tipo**: Usuario final
    - **Responsabilidades**: Subir archivos, seleccionar destino, descargar resultados
    - **Criterio de éxito**: Completar una migración exitosa en menos de 5 minutos para archivos de tamaño medio

    **Administrador:**
    - **Representante**: Personal de TI con rol admin
    - **Descripción**: Persona encargada de gestionar usuarios y monitorear el sistema
    - **Tipo**: Administrador del sistema
    - **Responsabilidades**: Crear/eliminar usuarios, monitorear accesos por IP, revisar logs
    - **Criterio de éxito**: Gestión efectiva de usuarios y detección oportuna de accesos sospechosos

    3.6	Necesidades de los interesados y usuarios

    | Necesidad | Prioridad | Solución Actual | Solución Propuesta |
    |:----------|:----------|:----------------|:-------------------|
    | Migrar datos entre motores SQL | Alta | Scripts manuales o herramientas comerciales | Módulo ETL automatizado con soporte multi-motor |
    | Detectar el tipo de base de datos | Alta | El usuario debe conocer el formato | Detección automática por análisis de contenido |
    | Interfaz visual para migración | Media | Línea de comandos | Interfaz web con progreso en tiempo real |
    | Preservar objetos SQL (vistas, triggers) | Media | Re-creación manual | Extracción y adaptación automática al motor destino |
    | Almacenar exportaciones en la nube | Baja | Descarga local y subida manual | Integración directa con GitHub |

<div style="page-break-after: always; visibility: hidden">\pagebreak</div>

4. <span id="_Toc52661349" class="anchor"></span>**Vista General del Producto**

    4.1	Perspectiva del producto

    MigradorBD es un producto independiente que funciona como una aplicación web autocontenida. No depende de otros sistemas para su operación básica, aunque se integra opcionalmente con servicios externos (Google OAuth, GitHub OAuth, GitHub API, servidor SMTP). El sistema opera bajo una arquitectura cliente-servidor donde:
    
    - **Cliente**: Navegador web que renderiza la interfaz HTML/CSS/JS.
    - **Servidor**: Aplicación Flask que procesa las solicitudes HTTP y WebSocket.
    - **Almacenamiento**: SQLite para autenticación y como almacenamiento intermedio ETL.

    4.2	Resumen de capacidades

    | Capacidad | Beneficio |
    |:----------|:----------|
    | Detección automática de motor de BD | Elimina la necesidad de que el usuario conozca el formato del archivo |
    | Soporte multi-motor (15+ motores) | Un solo sistema para todas las necesidades de migración |
    | Proceso ETL completo | Extracción, transformación y carga automatizadas |
    | Preservación de objetos SQL | Vistas, triggers, procedimientos y funciones se migran junto con los datos |
    | Autenticación OAuth | Login rápido y seguro con Google o GitHub |
    | Integración con GitHub | Almacenamiento y versionamiento de exportaciones en la nube |
    | Comunicación en tiempo real | El usuario ve el progreso de la migración en tiempo real vía WebSocket |
    | Panel de administración | Gestión de usuarios, monitoreo de IPs y logs del sistema |
    | Historial de migraciones | Registro detallado de todas las migraciones realizadas |

    4.3	Suposiciones y dependencias

    - Se asume que el usuario tiene acceso a un navegador web moderno.
    - Se asume disponibilidad de conexión a internet para funcionalidades OAuth y GitHub.
    - El sistema depende de Python 3.12+ y las bibliotecas listadas en requirements.txt.
    - Para producción, se requiere un VPS con Ubuntu 22.04+ y Nginx.

    4.4	Costos y precios

    El sistema es gratuito y de código abierto. Los únicos costos asociados son:
    - Servidor VPS para producción (~S/. 40/mes).
    - Dominio web (opcional, ~S/. 50/año).
    
    4.5	Licenciamiento e instalación

    El software se distribuye como código abierto. La instalación se realiza mediante:
    1. Clonar el repositorio.
    2. Instalar dependencias: `pip install -r requirements.txt`.
    3. Configurar variables de entorno (`.env`).
    4. Ejecutar: `python run.py`.

<div style="page-break-after: always; visibility: hidden">\pagebreak</div>

5. <span id="_Toc52661350" class="anchor"></span>**Características del producto**

    Las características principales de MigradorBD son:

    - **CP-01: Carga de archivos de base de datos**: Soporte para archivos .db, .sqlite, .sql, .json, .ndjson, .csv, .xlsx, .xls, .bak, .cql con un límite de 500 MB.
    - **CP-02: Detección automática de motor**: Análisis inteligente del contenido del archivo usando patrones sintácticos (CREATE TABLE, AUTO_INCREMENT, SERIAL, IDENTITY, etc.) para identificar MySQL, PostgreSQL, SQL Server, Oracle, BigQuery, Snowflake, Redshift, Cassandra, MongoDB, Elasticsearch y SQLite.
    - **CP-03: Extracción de esquema**: Descubrimiento automático de tablas, columnas, claves primarias, claves foráneas, índices, vistas, triggers, procedimientos almacenados y funciones.
    - **CP-04: Transformación de datos**: Limpieza de DataFrames, normalización de nombres de columnas, mapeo de tipos de datos entre motores y eliminación de filas nulas.
    - **CP-05: Generación de exportación multi-formato**: SQL nativo para cada motor, JSON para MongoDB, NDJSON para Elasticsearch, CQL para Cassandra, comandos HSET para Redis, y archivo .db para SQLite.
    - **CP-06: Autenticación multi-proveedor**: Registro local con verificación por email, login con Google OAuth, login con GitHub OAuth, y gestión de sesiones seguras.
    - **CP-07: Integración con GitHub**: Listar repositorios, crear nuevos repositorios, y subir archivos de migración directamente desde la interfaz web.
    - **CP-08: Panel de administración**: Gestión de usuarios (crear admin, eliminar usuario con notificación por email), monitoreo de accesos por IP, y logs del sistema.
    - **CP-09: Historial de migraciones**: Registro cronológico de todas las migraciones realizadas con métricas de rendimiento.
    - **CP-10: Comunicación en tiempo real**: Emisión de eventos WebSocket para notificar progreso de migración, errores y completación.

<div style="page-break-after: always; visibility: hidden">\pagebreak</div>

6. <span id="_Toc52661351" class="anchor"></span>**Restricciones**

    - El sistema está desarrollado en Python 3.12+ con Flask y no puede ejecutarse en versiones anteriores de Python.
    - El tamaño máximo de archivo es de 500 MB (configurable en `Config.MAX_CONTENT_LENGTH`).
    - La migración de archivos .bak binarios de SQL Server requiere restauración previa en un servidor SQL Server.
    - La funcionalidad de OAuth requiere conexión a internet y configuración previa de credenciales en Google Cloud Console y GitHub Developer Settings.
    - En Windows, el modo asíncrono de SocketIO se limita a threading (no eventlet/gevent).
    - El proceso de migración se ejecuta de forma síncrona en el servidor; migraciones muy grandes pueden agotar el tiempo de espera del navegador.

<div style="page-break-after: always; visibility: hidden">\pagebreak</div>

7. <span id="_Toc52661352" class="anchor"></span>**Rangos de Calidad**

    | Atributo de Calidad | Rango Aceptable | Métrica |
    |:--------------------|:----------------|:--------|
    | Rendimiento | Migración de archivo de 50MB en menos de 60 segundos | Tiempo de procesamiento |
    | Usabilidad | Completar migración en menos de 5 pasos | Número de clics/pasos |
    | Confiabilidad | 99% de disponibilidad del servicio web | Uptime |
    | Compatibilidad | Soporte para al menos 10 motores destino | Número de motores soportados |
    | Precisión | 100% de registros migrados sin pérdida de datos | Ratio extraídos/cargados |
    | Seguridad | Contraseñas hasheadas, sesiones seguras, HTTPS | Cumplimiento de OWASP |

<div style="page-break-after: always; visibility: hidden">\pagebreak</div>

8. <span id="_Toc52661353" class="anchor"></span>**Precedencia y Prioridad**

    | Prioridad | Característica | Justificación |
    |:----------|:---------------|:-------------|
    | 1 - Crítica | Extracción y detección de motor | Sin esto, no hay migración posible |
    | 2 - Alta | Carga y generación de SQL destino | Funcionalidad core del ETL |
    | 3 - Alta | Interfaz web con WebSocket | Experiencia de usuario esencial |
    | 4 - Media | Autenticación y control de roles | Seguridad del sistema |
    | 5 - Media | Preservación de objetos SQL | Valor agregado diferenciador |
    | 6 - Baja | Integración con GitHub | Funcionalidad complementaria |
    | 7 - Baja | Panel de administración | Gestión operativa |

<div style="page-break-after: always; visibility: hidden">\pagebreak</div>

9. <span id="_Toc52661354" class="anchor"></span>**Otros requerimientos del producto**

    **a) Estándares aplicables:**
    - OAuth 2.0 para autenticación con proveedores externos.
    - HTTPS para comunicación segura en producción.
    - WCAG 2.1 nivel AA para accesibilidad web.

    **b) Estándares legales:**
    - Ley N° 29733 (Ley de Protección de Datos Personales del Perú).
    - Cumplimiento de políticas de uso de API de Google y GitHub.

    **c) Estándares de comunicación:**
    - HTTP/HTTPS para comunicación cliente-servidor.
    - WebSocket (Socket.IO) para comunicación en tiempo real.
    - REST API para endpoints de la aplicación.

    **d) Estándares de cumplimiento de la plataforma:**
    - Compatibilidad con navegadores modernos (Chrome 90+, Firefox 88+, Edge 90+, Safari 14+).
    - Responsive design para acceso desde dispositivos móviles.

    **e) Estándares de calidad y seguridad:**
    - OWASP Top 10 para prevención de vulnerabilidades web.
    - Hashing de contraseñas con Werkzeug scrypt.
    - Cookies con HttpOnly, Secure y SameSite=Lax.
    - Aislamiento de archivos por usuario (carpetas de upload separadas).

<div style="page-break-after: always; visibility: hidden">\pagebreak</div>

<span id="_Toc52661355" class="anchor"></span>**CONCLUSIONES**

MigradorBD representa una solución integral para el problema de la migración de datos entre bases de datos heterogéneas. El sistema cubre el ciclo completo del proceso ETL con una interfaz web intuitiva, detección automática de motores y soporte para más de 15 motores destino. La arquitectura modular del sistema (extracción, transformación, carga, utilidades) facilita la extensibilidad y el mantenimiento del código. La integración con servicios externos (OAuth, GitHub) añade valor al permitir autenticación sin fricción y almacenamiento en la nube de las exportaciones.

<div style="page-break-after: always; visibility: hidden">\pagebreak</div>

<span id="_Toc52661356" class="anchor"></span>**RECOMENDACIONES**

- Implementar soporte para conexiones directas a servidores de bases de datos (no solo archivos locales) para ampliar el alcance del sistema.
- Agregar procesamiento asíncrono con colas de tareas (Celery/Redis) para migraciones de archivos muy grandes.
- Implementar pruebas unitarias automatizadas para todos los módulos del pipeline ETL.
- Considerar la implementación de un sistema de plugins para facilitar la adición de nuevos motores de bases de datos.
- Agregar soporte para migración incremental (solo cambios desde la última migración).

<div style="page-break-after: always; visibility: hidden">\pagebreak</div>

<span id="_Toc52661357" class="anchor"></span>**BIBLIOGRAFIA**

- Pressman, R. S. (2014). *Ingeniería del Software: Un Enfoque Práctico* (8ª ed.). McGraw-Hill.
- Sommerville, I. (2016). *Software Engineering* (10ª ed.). Pearson.
- Kimball, R., & Ross, M. (2013). *The Data Warehouse Toolkit: The Definitive Guide to Dimensional Modeling* (3ª ed.). Wiley.
- Grinberg, M. (2018). *Flask Web Development: Developing Web Applications with Python* (2ª ed.). O'Reilly Media.

<div style="page-break-after: always; visibility: hidden">\pagebreak</div>

<span id="_Toc52661358" class="anchor"></span>**WEBGRAFIA**

- Flask Documentation. https://flask.palletsprojects.com/
- SQLAlchemy Documentation. https://docs.sqlalchemy.org/
- Authlib Documentation. https://docs.authlib.org/
- Flask-SocketIO Documentation. https://flask-socketio.readthedocs.io/
- Pandas Documentation. https://pandas.pydata.org/docs/
- Google OAuth 2.0 Documentation. https://developers.google.com/identity/protocols/oauth2
- GitHub OAuth Documentation. https://docs.github.com/en/developers/apps/building-oauth-apps

<div style="page-break-after: always; visibility: hidden">\pagebreak</div>
