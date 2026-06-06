![C:\Users\EPIS\Documents\upt.png](media/image1.png){width="1.0879997812773403in" height="1.4625557742782151in"}

**UNIVERSIDAD PRIVADA DE TACNA**

**FACULTAD DE INGENIERIA**

**Escuela Profesional de Ingeniería de Sistemas**

**Informe Final**

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

INDICE GENERAL

1.  [Antecedentes](#antecedentes)

2.  [Planteamiento del Problema](#planteamiento-problema)

    a.  [Problema](#problema)

    b.  [Justificación](#justificacion)

    c.  [Alcance](#alcance-pf)

3.  [Objetivos](#objetivos-pf)

4.  [Marco Teórico](#marco-teorico)

5.  [Desarrollo de la Solución](#desarrollo-solucion)

    a.  [Análisis de Factibilidad](#factibilidad-pf)

    b.  [Tecnología de Desarrollo](#tecnologia-desarrollo)

    c.  [Metodología de implementación](#metodologia-implementacion)

6.  [Cronograma](#cronograma)

7.  [Presupuesto](#presupuesto-pf)

8.  [Conclusiones](#conclusiones-pf)

[Recomendaciones](#recomendaciones-pf)

[Bibliografía](#bibliografia-pf)

[Anexos](#anexos-pf)

---

<span id="antecedentes"></span>
## 1. Antecedentes

La migración de bases de datos es un proceso crítico en el ciclo de vida de los sistemas de información. A medida que las organizaciones evolucionan, surge la necesidad de migrar datos entre diferentes motores de bases de datos por diversas razones: actualización tecnológica, migración a la nube, consolidación de sistemas, cambio de proveedor o integración entre plataformas heterogéneas.

Existen antecedentes relevantes en el ámbito de herramientas de migración:

- **AWS Database Migration Service (DMS)**: Servicio de Amazon Web Services para migración de bases de datos en la nube. Soporta migración entre motores homogéneos y heterogéneos. Limitación: requiere infraestructura AWS y tiene costos asociados por hora de uso.

- **Azure Database Migration Service**: Herramienta de Microsoft para migración hacia Azure SQL Database. Limitación: enfocada principalmente en migración hacia el ecosistema Microsoft.

- **Oracle Data Pump**: Utilidad nativa de Oracle para exportación/importación de datos. Limitación: específica para Oracle, no soporta otros motores.

- **MySQL Workbench Migration Wizard**: Herramienta de migración incluida en MySQL Workbench. Limitación: solo soporta migración hacia MySQL desde algunos motores.

- **pgLoader**: Herramienta de código abierto para cargar datos en PostgreSQL. Limitación: solo soporta PostgreSQL como destino.

Ninguna de las herramientas existentes ofrece una solución web unificada, gratuita y de código abierto que soporte migración entre más de 15 motores de bases de datos con detección automática del motor de origen.

---

<span id="planteamiento-problema"></span>
## 2. Planteamiento del Problema

<span id="problema"></span>
### a. Problema

Las organizaciones y profesionales de TI enfrentan la necesidad frecuente de migrar datos entre diferentes sistemas de gestión de bases de datos. Este proceso presenta múltiples desafíos:

1. **Heterogeneidad de motores**: Cada SGBD tiene su propia sintaxis SQL, sistema de tipos de datos, y características específicas (AUTO_INCREMENT en MySQL, SERIAL en PostgreSQL, IDENTITY en SQL Server, etc.).

2. **Costo de herramientas**: Las soluciones comerciales (AWS DMS, Azure Migration, Oracle Data Pump) tienen costos significativos que pueden ser prohibitivos para pequeñas empresas y proyectos académicos.

3. **Complejidad del proceso**: La migración manual requiere conocimiento especializado de ambos motores, es propensa a errores y difícil de reproducir.

4. **Falta de detección automática**: La mayoría de herramientas requieren que el usuario identifique manualmente el formato del archivo de origen.

5. **Soporte limitado**: Las herramientas existentes generalmente soportan migración entre 2-3 motores específicos, no entre ecosistemas completos (SQL, NoSQL, archivos).

<span id="justificacion"></span>
### b. Justificación

El desarrollo de MigradorBD se justifica por las siguientes razones:

- **Necesidad del mercado**: No existe una herramienta web gratuita y de código abierto que soporte migración multi-motor con detección automática.
- **Democratización del acceso**: Una herramienta gratuita permite que organizaciones de todos los tamaños y estudiantes accedan a funcionalidades de migración profesional.
- **Eficiencia operativa**: La automatización del proceso ETL reduce el tiempo de migración de días a minutos.
- **Valor académico**: El proyecto integra múltiples disciplinas de la ingeniería de software: bases de datos, desarrollo web, autenticación, APIs REST, WebSocket, despliegue en producción.

<span id="alcance-pf"></span>
### c. Alcance

**El sistema incluye:**
- Migración desde archivos: SQLite, SQL (MySQL, PostgreSQL, SQL Server, Oracle, BigQuery, Snowflake, Redshift), JSON, NDJSON, CSV, Excel, CQL.
- Exportación hacia 15+ motores: MySQL, PostgreSQL, SQL Server, Oracle, SQLite, MongoDB, Elasticsearch, Cassandra, Redis, Snowflake, BigQuery, Redshift, MariaDB, Db2, Azure SQL.
- Detección automática del motor de origen basada en análisis de contenido.
- Preservación de objetos SQL: vistas, triggers, procedimientos almacenados, funciones, índices.
- Autenticación multi-proveedor: registro local con verificación por email, Google OAuth, GitHub OAuth.
- Integración con GitHub: listar repos, crear repos, subir archivos.
- Panel de administración con gestión de usuarios y monitoreo de IPs.
- Historial de migraciones con métricas de rendimiento.
- Comunicación en tiempo real vía WebSocket.

**El sistema NO incluye:**
- Conexión directa a servidores de bases de datos remotos (solo procesa archivos).
- Migración incremental o en tiempo real.
- Soporte para archivos .bak binarios de SQL Server (requieren restauración previa).
- Interfaz móvil nativa (aunque la web es responsive).

---

<span id="objetivos-pf"></span>
## 3. Objetivos

**Objetivo General:**

Desarrollar un sistema web de migración de bases de datos que permita la extracción, transformación y carga de datos entre múltiples motores de bases de datos de forma automatizada, segura y eficiente.

**Objetivos Específicos:**

1. Implementar un módulo de detección automática (`utilidades/detector.py`) que identifique el tipo de motor de base de datos a partir del análisis del contenido del archivo, soportando SQLite, MySQL, PostgreSQL, SQL Server, Oracle, BigQuery, Snowflake, Redshift, Cassandra, MongoDB, Elasticsearch, CSV y Excel.

2. Desarrollar un módulo de extracción (`extraccion/conector.py`) capaz de parsear scripts SQL con expresiones regulares robustas para extraer esquemas completos (tablas, columnas, claves, índices) y datos (INSERT INTO), además de soportar archivos binarios SQLite, JSON, CSV y Excel.

3. Construir un módulo de carga (`carga/cargador.py`) que genere exportaciones SQL nativas para cada motor destino con traducción correcta de tipos de datos, y exportaciones especializadas para MongoDB (JSON), Elasticsearch (NDJSON), Cassandra (CQL) y Redis (HSET).

4. Implementar un sistema de autenticación completo (`app/auth.py`, `app/oauth.py`) con registro local, verificación por email, login con Google OAuth y GitHub OAuth, control de roles (usuario/admin) y gestión de sesiones seguras.

5. Desarrollar una interfaz web interactiva con 12 plantillas HTML, comunicación en tiempo real vía Flask-SocketIO, y diseño responsive.

6. Integrar el sistema con la API de GitHub (`app/routes.py`) para permitir listar repositorios, crear nuevos repositorios y subir archivos de migración directamente desde la interfaz web.

7. Desplegar el sistema en producción en un VPS Ubuntu con Nginx, Gunicorn, Supervisor y certificado SSL.

---

<span id="marco-teorico"></span>
## 4. Marco Teórico

### 4.1. Proceso ETL (Extracción, Transformación y Carga)

El proceso ETL es un paradigma fundamental en la gestión de datos que consiste en tres fases:

- **Extracción (Extract)**: Obtención de datos desde uno o más sistemas de origen. En MigradorBD, esto se implementa en `ConectorOrigen` que soporta múltiples formatos de entrada.
- **Transformación (Transform)**: Modificación de los datos para adaptarlos al formato del destino. En MigradorBD, `MapeadorDatos` normaliza nombres de columnas, convierte tipos y elimina datos nulos.
- **Carga (Load)**: Inserción de los datos transformados en el sistema de destino. En MigradorBD, `CargadorDestino` genera exportaciones nativas para cada motor.

### 4.2. Sistemas de Gestión de Bases de Datos

El sistema soporta tres categorías de SGBD:

- **Relacionales (SQL)**: MySQL, PostgreSQL, Microsoft SQL Server, Oracle, SQLite, MariaDB, Snowflake, BigQuery, Redshift, Db2, Azure SQL. Usan esquemas tabulares con tipos de datos específicos.
- **NoSQL documentales**: MongoDB (JSON), Elasticsearch (NDJSON). Almacenan documentos sin esquema fijo.
- **NoSQL clave-valor**: Redis (HSET). Almacenan pares clave-valor.
- **NoSQL columnar**: Apache Cassandra (CQL). Optimizado para escrituras masivas.

### 4.3. Detección automática de motores

El sistema implementa detección basada en análisis heurístico del contenido:
- **SQLite**: Verificación binaria intentando abrir el archivo como base de datos SQLite.
- **SQL**: Análisis de patrones sintácticos con regex (AUTO_INCREMENT → MySQL, SERIAL → PostgreSQL, IDENTITY → SQL Server, VARCHAR2 → Oracle, etc.).
- **JSON/NDJSON**: Parsing JSON con validación de estructura.
- **CSV/Excel**: Intentos de lectura con Pandas.

### 4.4. Flask y Flask-SocketIO

Flask es un microframework web para Python que proporciona un núcleo minimalista extensible con plugins. Flask-SocketIO añade soporte para WebSocket, permitiendo comunicación bidireccional en tiempo real entre el servidor y el cliente.

### 4.5. OAuth 2.0

OAuth 2.0 es un protocolo estándar de autorización que permite a los usuarios autenticarse con proveedores externos (Google, GitHub) sin compartir sus credenciales. El sistema utiliza Authlib para implementar el flujo de autorización.

---

<span id="desarrollo-solucion"></span>
## 5. Desarrollo de la Solución

<span id="factibilidad-pf"></span>
### a. Análisis de Factibilidad

El análisis completo de factibilidad se encuentra en el documento FD01 (Informe de Factibilidad). En resumen:

- **Factibilidad Técnica**: ✅ Todas las tecnologías son de código abierto y maduras.
- **Factibilidad Económica**: ✅ Costo total: S/. 6,590.00. B/C = 1.21, VAN = S/. 13,304.82.
- **Factibilidad Operativa**: ✅ Interfaz intuitiva, detección automática, documentación completa.
- **Factibilidad Legal**: ✅ Sin conflictos legales, licencias permisivas.

<span id="tecnologia-desarrollo"></span>
### b. Tecnología de Desarrollo

| Categoría | Tecnología | Versión | Propósito |
|:----------|:-----------|:--------|:----------|
| Lenguaje | Python | 3.12+ | Lenguaje principal |
| Framework Web | Flask | 2.3.3 | Servidor web |
| WebSocket | Flask-SocketIO | 5.3.0 | Comunicación en tiempo real |
| ORM | SQLAlchemy | 2.0.23 | Acceso a bases de datos |
| Datos | Pandas | 2.1.1 | Manipulación de DataFrames |
| Datos | NumPy | 1.26.4 | Operaciones numéricas |
| Excel | OpenPyXL | 3.1.3 | Lectura/escritura Excel |
| OAuth | Authlib | 1.2.0 | Autenticación OAuth 2.0 |
| Seguridad | Werkzeug | 2.3.7 | Hashing de contraseñas |
| Seguridad | Bcrypt | 4.0.1 | Hashing adicional |
| Email | Flask-Mail | 0.9.1 | Envío de emails |
| GitHub | PyGithub | 1.59.1 | API de GitHub |
| HTTP | Requests | 2.31.0 | Cliente HTTP |
| Config | python-dotenv | 1.0.0 | Variables de entorno |
| Config | PyYAML | 6.0.1 | Archivos de configuración |
| Servidor | Gunicorn | 21.2.0 | Servidor WSGI producción |
| Async | Eventlet | 0.33.3 | Servidor asíncrono |
| Proxy | Nginx | - | Proxy reverso |
| Procesos | Supervisor | - | Gestión de procesos |

<span id="metodologia-implementacion"></span>
### c. Metodología de implementación

El proyecto se desarrolló siguiendo una metodología ágil adaptada, con las siguientes etapas:

**Iteración 1 - Core ETL (Semanas 1-4):**
- Implementación del detector de bases de datos.
- Desarrollo del conector de origen para SQLite y SQL genérico.
- Implementación del mapeador de datos.
- Desarrollo del cargador de destino con generación SQL.
- Pruebas de detección con archivos de prueba (`tests/test_deteccion_bd.py`).

**Iteración 2 - Interfaz Web (Semanas 5-8):**
- Diseño de plantillas HTML (12 vistas).
- Implementación de rutas Flask (Blueprint principal).
- Integración de Flask-SocketIO para progreso en tiempo real.
- Desarrollo del flujo de carga de archivo → detección → migración → descarga.

**Iteración 3 - Autenticación y Seguridad (Semanas 9-12):**
- Sistema de registro con verificación por email.
- Integración de Google OAuth y GitHub OAuth.
- Control de roles (usuario/admin).
- Panel de administración.
- Aislamiento de archivos por usuario.

**Iteración 4 - GitHub e Integración (Semanas 13-16):**
- Integración con GitHub API (listar, crear repos, subir archivos).
- Historial de migraciones.
- Monitoreo de IPs.
- Perfil de usuario.
- Scripts de despliegue para producción.
- Documentación.

---

<span id="cronograma"></span>
## 6. Cronograma

| Semana | Actividad | Responsable |
|:-------|:----------|:------------|
| 1-2 | Análisis de requerimientos y diseño de arquitectura | JLM + UHR |
| 3-4 | Desarrollo del detector de BD y conector de origen | JLM |
| 5-6 | Desarrollo del mapeador y cargador de destino | JLM |
| 7-8 | Diseño e implementación de la interfaz web | UHR |
| 9-10 | Sistema de autenticación y OAuth | UHR |
| 11-12 | Integración WebSocket y pruebas ETL | JLM |
| 13-14 | Integración con GitHub y panel de administración | UHR |
| 15 | Despliegue en producción y pruebas finales | JLM + UHR |
| 16 | Documentación y entrega final | JLM + UHR |

---

<span id="presupuesto-pf"></span>
## 7. Presupuesto

| Concepto | Costo (S/.) |
|:---------|:------------|
| Costos Generales (útiles de oficina) | 100.00 |
| Costos Operativos (internet, electricidad) | 520.00 |
| Costos del Ambiente (VPS, dominio) | 210.00 |
| Costos de Personal (2 desarrolladores, 16 semanas) | 5,760.00 |
| **TOTAL** | **6,590.00** |

---

<span id="conclusiones-pf"></span>
## 8. Conclusiones

1. Se logró desarrollar exitosamente el sistema MigradorBD, una aplicación web integral de migración de bases de datos que implementa un proceso ETL completo con soporte para más de 15 motores de bases de datos destino.

2. El módulo de detección automática (`DetectorBaseDatos`) identifica correctamente el motor de origen analizando el contenido del archivo, no solo su extensión, lo que mejora significativamente la experiencia del usuario.

3. El módulo de extracción (`ConectorOrigen`) parsea exitosamente scripts SQL de múltiples motores mediante expresiones regulares robustas, extrayendo esquemas completos incluyendo vistas, triggers, procedimientos almacenados y funciones.

4. El módulo de carga (`CargadorDestino`) genera exportaciones SQL nativas con traducción correcta de tipos de datos para cada motor destino (VARCHAR2 para Oracle, TEXT para PostgreSQL, NVARCHAR para SQL Server, STRING para BigQuery, etc.), además de formatos especializados (JSON, NDJSON, CQL, Redis).

5. La integración de autenticación multi-proveedor (local + Google OAuth + GitHub OAuth) con verificación por email y control de roles proporciona un sistema de seguridad robusto.

6. La integración con GitHub permite a los usuarios almacenar y versionar sus exportaciones directamente en repositorios, añadiendo valor al flujo de trabajo de migración.

7. La arquitectura modular del sistema (extracción → transformación → carga) facilita la extensión futura con nuevos motores de bases de datos.

---

<span id="recomendaciones-pf"></span>
## Recomendaciones

1. **Conexión directa a servidores**: Implementar soporte para conexiones directas a servidores de bases de datos (no solo archivos locales) utilizando SQLAlchemy con los drivers correspondientes.

2. **Procesamiento asíncrono**: Integrar Celery con Redis como broker de mensajes para procesar migraciones grandes en segundo plano.

3. **Migración incremental**: Implementar detección de cambios para permitir migraciones parciales (solo datos nuevos o modificados).

4. **Pruebas automatizadas**: Ampliar la cobertura de pruebas unitarias y de integración para todos los módulos del pipeline ETL.

5. **Contenedorización**: Crear un Dockerfile y docker-compose.yml para facilitar el despliegue en cualquier entorno.

6. **Sistema de plugins**: Diseñar un sistema de plugins que permita agregar soporte para nuevos motores sin modificar el código fuente principal.

---

<span id="bibliografia-pf"></span>
## Bibliografía

- Pressman, R. S. (2014). *Ingeniería del Software: Un Enfoque Práctico* (8ª ed.). McGraw-Hill.
- Sommerville, I. (2016). *Software Engineering* (10ª ed.). Pearson.
- Kimball, R., & Ross, M. (2013). *The Data Warehouse Toolkit* (3ª ed.). Wiley.
- Grinberg, M. (2018). *Flask Web Development* (2ª ed.). O'Reilly Media.
- Copeland, R. (2008). *Essential SQLAlchemy*. O'Reilly Media.

---

<span id="anexos-pf"></span>
## Anexos

Anexo 01 – Informe de Factibilidad (FD01-Informe-Factibilidad.md)

Anexo 02 – Documento de Visión (FD02-Informe-Vision.md)

Anexo 03 – Documento SRS (FD03-EPIS-Informe Especificación Requerimientos.md)

Anexo 04 – Documento SAD (FD04-EPIS-Informe Arquitectura de Software.md)

Anexo 05 – Manuales de despliegue (docs/DEPLOY_UBUNTU.md, docs/QUICK_START.md)

Anexo 06 – Documentación de autenticación (docs/README_AUTH.md, docs/OAUTH_SETUP.md)
