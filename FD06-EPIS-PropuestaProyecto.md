![C:\Users\EPIS\Documents\upt.png](media/image1.png){width="1.0879997812773403in" height="1.4625557742782151in"}

**UNIVERSIDAD PRIVADA DE TACNA**

**FACULTAD DE INGENIERIA**

**Escuela Profesional de Ingeniería de Sistemas**

**Propuesta del Proyecto *MigradorBD - Sistema de Migración de Bases de Datos***

Curso: *Ingeniería de Software (SI783)*

Docente: *Mag. Patrick José Cuadros Quiroga*

Integrantes:

***LLica Mamani, Jimmy Mijair***
***Halanocca Rojas, Usher Damiron***

**Tacna – Perú**

***2026***

**\**

**Proyecto**

***MigradorBD – Sistema Integral de Migración de Bases de Datos, Tacna, 2026***

**Presentado por:**

***LLica Mamani, Jimmy Mijair – Desarrollador Backend/ETL***
***Halanocca Rojas, Usher Damiron – Desarrollador Frontend/Auth***

***Junio 2026***

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

# Tabla de contenido {#tabla-de-contenido .TOC-Heading}

[Resumen Ejecutivo](#resumen-ejecutivo)

I Propuesta narrativa

1.  [Planteamiento del Problema](#planteamiento-problema-pp)

2.  [Justificación del proyecto](#justificacion-pp)

3.  [Objetivo general](#objetivo-general-pp)

4.  [Beneficios](#beneficios-pp)

5.  [Alcance](#alcance-pp)

6.  [Requerimientos del sistema](#requerimientos-pp)

7.  [Restricciones](#restricciones-pp)

8.  [Supuestos](#supuestos-pp)

9.  [Resultados esperados](#resultados-esperados-pp)

10. [Metodología de implementación](#metodologia-pp)

11. [Actores claves](#actores-claves-pp)

12. [Papel y responsabilidades del personal](#responsabilidades-pp)

13. [Plan de monitoreo y evaluación](#monitoreo-pp)

14. [Cronograma del proyecto](#cronograma-pp)

15. [Hitos de entregables](#hitos-pp)

II Presupuesto

1.  [Planteamiento de aplicación del presupuesto](#presupuesto-aplicacion)

2.  [Presupuesto](#presupuesto-detalle)

3.  [Análisis de Factibilidad](#factibilidad-pp)

4.  [Evaluación Financiera](#evaluacion-financiera)

[Anexo 01 – Requerimientos del Sistema MigradorBD](#anexo-requerimientos)

**\**

<span id="resumen-ejecutivo"></span>
## RESUMEN EJECUTIVO

<table style="width:92%;">
<colgroup>
<col style="width: 44%" />
<col style="width: 47%" />
</colgroup>
<thead>
<tr>
<th colspan="2"><p><strong>Nombre del Proyecto propuesto</strong>:</p>
<p><em>MigradorBD – Sistema Integral de Migración de Bases de Datos, Tacna, 2026</em></p></th>
</tr>
</thead>
<tbody>
<tr>
<td colspan="2"><p><strong>Propósito del Proyecto y Resultados esperados:</strong></p>
<p>El propósito del proyecto es desarrollar un sistema web integral de migración de bases de datos que permita la extracción, transformación y carga (ETL) entre múltiples motores de bases de datos, con detección automática del motor de origen, autenticación segura y interfaz web interactiva.</p>
<p>Los resultados esperados son:</p>
<ul>
<li><p>Sistema web funcional que permita migrar datos entre más de 15 motores de bases de datos.</p></li>
<li><p>Detección automática del tipo de motor basada en análisis de contenido del archivo.</p></li>
<li><p>Preservación de objetos SQL (vistas, triggers, procedimientos, funciones, índices) durante la migración.</p></li>
<li><p>Autenticación multi-proveedor con Google OAuth, GitHub OAuth y registro local con verificación por email.</p></li>
<li><p>Integración con GitHub para almacenamiento y versionamiento de exportaciones.</p></li>
</ul></td>
</tr>
<tr>
<td colspan="2"><p><strong>Población Objetivo:</strong></p>
<p>Administradores de bases de datos, desarrolladores de software, empresas en proceso de modernización tecnológica, estudiantes y docentes de ingeniería de sistemas.</p></td>
</tr>
<tr>
<td><p><strong>Monto de Inversión (En Soles):</strong></p>
<p><em><strong>S/. 6,590.00</strong></em></p></td>
<td><p><strong>Duración del Proyecto (En Meses):</strong></p>
<p><em><strong>4 meses (Marzo – Junio 2026)</strong></em></p></td>
</tr>
</tbody>
</table>

---

## I. PROPUESTA NARRATIVA

<span id="planteamiento-problema-pp"></span>
### 1. Planteamiento del Problema

En el entorno actual de desarrollo de software y administración de sistemas, las organizaciones enfrentan la necesidad constante de migrar datos entre diferentes motores de bases de datos. Las razones incluyen actualización tecnológica, migración a la nube, consolidación de sistemas, cambio de proveedor o integración entre plataformas heterogéneas.

Las herramientas existentes presentan limitaciones significativas:
- **Costo elevado**: AWS DMS, Azure Database Migration y Oracle Data Pump tienen costos de licenciamiento que pueden ser prohibitivos.
- **Soporte limitado**: La mayoría soporta solo 2-3 motores específicos.
- **Complejidad**: Requieren configuración avanzada y conocimiento especializado.
- **Sin detección automática**: El usuario debe identificar manualmente el formato del archivo.
- **Sin interfaz web unificada**: Operan desde línea de comandos o interfaces de escritorio.

<span id="justificacion-pp"></span>
### 2. Justificación del proyecto

La justificación del proyecto se fundamenta en:

- **Necesidad real**: Las migraciones de bases de datos son cada vez más frecuentes en un ecosistema tecnológico diverso.
- **Vacío en el mercado**: No existe una herramienta web gratuita y de código abierto con soporte para 15+ motores.
- **Valor educativo**: El proyecto integra conceptos avanzados de bases de datos, desarrollo web, seguridad, APIs y despliegue.
- **Impacto social**: Democratiza el acceso a herramientas profesionales de migración.

<span id="objetivo-general-pp"></span>
### 3. Objetivo general

Desarrollar un sistema web de migración de bases de datos que automatice el proceso ETL (Extracción, Transformación y Carga) entre múltiples motores, ofreciendo detección automática del motor de origen, autenticación segura, interfaz web interactiva con progreso en tiempo real e integración con GitHub.

<span id="beneficios-pp"></span>
### 4. Beneficios

**Beneficios tangibles:**
- Reducción del tiempo de migración de 2-5 días a menos de 1 hora.
- Eliminación de costos de licencias comerciales (ahorro estimado: $500-$5,000 USD/año).
- Reducción de errores humanos en un 80%.
- Soporte para 15+ motores destino en una sola herramienta.

**Beneficios intangibles:**
- Mejora en la eficiencia operativa del equipo de TI.
- Democratización del acceso a herramientas de migración profesional.
- Ventaja competitiva por ser una solución multi-motor sin precedentes.
- Valor educativo para la formación en ingeniería de software.

<span id="alcance-pp"></span>
### 5. Alcance

El proyecto abarca el desarrollo completo de una aplicación web con:
- Pipeline ETL completo (extracción, transformación, carga).
- Detección automática de 13 tipos de motor/formato de origen.
- Generación de exportaciones para 15+ motores destino.
- Sistema de autenticación con 3 proveedores (local, Google, GitHub).
- Integración con GitHub API.
- Panel de administración y monitoreo.
- Despliegue en producción con Nginx + Gunicorn.

<span id="requerimientos-pp"></span>
### 6. Requerimientos del sistema

**Hardware mínimo:**
- Procesador: 2 cores
- RAM: 4 GB
- Almacenamiento: 10 GB disponibles
- Conexión a internet

**Software requerido:**
- Python 3.12+
- Flask 2.3.3 + Flask-SocketIO 5.3.0
- SQLAlchemy 2.0.23 + Pandas 2.1.1
- Authlib 1.2.0 + Werkzeug 2.3.7
- Nginx + Gunicorn (producción)

<span id="restricciones-pp"></span>
### 7. Restricciones

- El sistema solo procesa archivos de base de datos; no se conecta directamente a servidores remotos.
- Tamaño máximo de archivo: 500 MB.
- Los archivos .bak binarios de SQL Server requieren restauración previa.
- OAuth requiere credenciales configuradas en Google Cloud Console y GitHub Developer Settings.
- En Windows, SocketIO opera en modo threading (no eventlet).

<span id="supuestos-pp"></span>
### 8. Supuestos

- Los usuarios tienen acceso a un navegador web moderno (Chrome, Firefox, Edge, Safari).
- Se dispone de conexión a internet para funcionalidades OAuth y GitHub.
- Los archivos de base de datos a migrar están en los formatos soportados.
- El equipo de desarrollo tiene competencias en Python, Flask y bases de datos.
- Se cuenta con acceso a un VPS Ubuntu para el despliegue en producción.

<span id="resultados-esperados-pp"></span>
### 9. Resultados esperados

| Resultado | Indicador | Meta |
|:----------|:----------|:-----|
| Sistema web funcional | Disponibilidad del servicio | 99% uptime |
| Detección correcta de motores | Tasa de detección exitosa | > 95% |
| Migración sin pérdida de datos | Ratio registros_cargados / extraídos | 100% |
| Tiempo de migración optimizado | Tiempo para archivo de 50 MB | < 60 segundos |
| Cobertura multi-motor | Número de motores destino soportados | ≥ 15 |
| Autenticación multi-proveedor | Proveedores de login | 3 (local, Google, GitHub) |

<span id="metodologia-pp"></span>
### 10. Metodología de implementación

Se utilizará una metodología ágil adaptada con iteraciones de 4 semanas:

- **Iteración 1 (Semanas 1-4)**: Core ETL – Detector, conector, mapeador, cargador.
- **Iteración 2 (Semanas 5-8)**: Interfaz Web – Plantillas HTML, rutas Flask, WebSocket.
- **Iteración 3 (Semanas 9-12)**: Autenticación – Registro, OAuth, roles, administración.
- **Iteración 4 (Semanas 13-16)**: Integración – GitHub, historial, despliegue, documentación.

Herramientas de gestión:
- **Control de versiones**: Git con GitHub.
- **Gestión de tareas**: Issues de GitHub.
- **Comunicación**: Reuniones semanales.
- **Documentación**: Markdown en repositorio.

<span id="actores-claves-pp"></span>
### 11. Actores claves

| Actor | Rol | Participación |
|:------|:----|:-------------|
| LLica Mamani, Jimmy Mijair | Desarrollador Backend/ETL | Diseño y desarrollo del pipeline ETL, detector de BD, pruebas, despliegue |
| Halanocca Rojas, Usher Damiron | Desarrollador Frontend/Auth | Interfaz web, autenticación, OAuth, integración GitHub, plantillas |
| Docente evaluador | Supervisor académico | Evaluación y retroalimentación |
| Usuarios de prueba | Validadores | Pruebas de usabilidad y funcionalidad |

<span id="responsabilidades-pp"></span>
### 12. Papel y responsabilidades del personal

**LLica Mamani, Jimmy Mijair – Desarrollador Backend/ETL:**

| Módulo | Archivo | Responsabilidad |
|:-------|:--------|:----------------|
| Detección | utilidades/detector.py | Implementar detección automática de 13 tipos de motor |
| Extracción | extraccion/conector.py | Desarrollar parseo de SQL, SQLite, JSON, CSV, Excel |
| Transformación | transformacion/mapeador.py | Implementar limpieza y mapeo de datos |
| Carga | carga/cargador.py | Desarrollar generación de exportaciones multi-formato |
| Pruebas | tests/ | Crear y ejecutar pruebas de detección y migración |
| Configuración | config/ | Definir configuración del sistema (YAML, .env) |
| Despliegue | despliegue/ | Scripts de despliegue en producción (Ubuntu, Nginx) |

**Halanocca Rojas, Usher Damiron – Desarrollador Frontend/Auth:**

| Módulo | Archivo | Responsabilidad |
|:-------|:--------|:----------------|
| Aplicación | app/__init__.py | Factory de aplicación Flask |
| Rutas | app/routes.py | Blueprint principal con todas las rutas |
| Autenticación | app/auth.py | Sistema de registro, login, roles, verificación |
| OAuth | app/oauth.py | Configuración de Google y GitHub OAuth |
| GitHub | app/github_integration.py | Integración con GitHub API |
| Modelos | app/models.py | Modelos de datos (dataclasses) |
| Vistas | app/templates/ | 12 plantillas HTML (Jinja2) |
| Estilos | app/static/ | CSS y JavaScript |
| SQL | sql/ | Script de inicialización de BD de autenticación |

**Horario de trabajo:**
- Lunes a Viernes: 4 horas (18:00 - 22:00)
- Sábados: 4 horas (09:00 - 13:00)
- Total: 24 horas/semana por integrante

<span id="monitoreo-pp"></span>
### 13. Plan de monitoreo y evaluación

| Fase | Criterio de evaluación | Evidencia | Responsable |
|:-----|:----------------------|:----------|:------------|
| Iteración 1 | Detector identifica correctamente 9/9 tipos SQL | Ejecución de test_deteccion_bd.py | JLM |
| Iteración 1 | ConectorOrigen extrae esquema de archivo de prueba | Log de tablas y columnas extraídas | JLM |
| Iteración 2 | Interfaz web muestra flujo completo de migración | Captura de pantalla de cada paso | UHR |
| Iteración 2 | WebSocket emite progreso de migración | Log de eventos SocketIO | UHR |
| Iteración 3 | Login con Google y GitHub funcional | Capturas de flujo OAuth | UHR |
| Iteración 3 | Panel admin gestiona usuarios | Captura de creación/eliminación de usuario | UHR |
| Iteración 4 | Subida de archivo a GitHub exitosa | URL del archivo en GitHub | UHR |
| Iteración 4 | Despliegue en VPS funcional | URL pública accesible | JLM |

<span id="cronograma-pp"></span>
### 14. Cronograma del proyecto

| Semana | Mar | Abr | May | Jun | Actividad |
|:-------|:---:|:---:|:---:|:---:|:----------|
| 1-2 | ██ | | | | Análisis y diseño |
| 3-4 | ██ | | | | Detector + Conector |
| 5-6 | | ██ | | | Mapeador + Cargador |
| 7-8 | | ██ | | | Interfaz web + WebSocket |
| 9-10 | | | ██ | | Autenticación + OAuth |
| 11-12 | | | ██ | | Integración + Pruebas |
| 13-14 | | | | ██ | GitHub + Admin |
| 15-16 | | | | ██ | Despliegue + Documentación |

<span id="hitos-pp"></span>
### 15. Hitos de entregables

| Hito | Fecha | Entregable |
|:-----|:------|:-----------|
| H1 | Semana 4 | Pipeline ETL funcional (detección + extracción + transformación + carga) |
| H2 | Semana 8 | Interfaz web completa con flujo de migración |
| H3 | Semana 12 | Sistema de autenticación multi-proveedor |
| H4 | Semana 14 | Integración con GitHub y panel de administración |
| H5 | Semana 16 | Despliegue en producción + documentación final |

---

## II. PRESUPUESTO

<span id="presupuesto-aplicacion"></span>
### 1. Planteamiento de aplicación del presupuesto

El presupuesto se distribuye en cuatro categorías: costos generales (materiales de oficina), costos operativos (servicios durante el desarrollo), costos del ambiente (infraestructura de producción) y costos de personal (recurso humano).

<span id="presupuesto-detalle"></span>
### 2. Presupuesto

| Categoría | Detalle | Costo (S/.) |
|:----------|:--------|:------------|
| **Costos Generales** | | |
| | Papel bond A4 (1 millar) | 25.00 |
| | USB 32GB (2 unidades) | 60.00 |
| | Útiles de escritorio | 15.00 |
| | **Subtotal** | **100.00** |
| **Costos Operativos** | | |
| | Internet (4 meses × S/.80) | 320.00 |
| | Energía eléctrica (4 meses × S/.50) | 200.00 |
| | **Subtotal** | **520.00** |
| **Costos del Ambiente** | | |
| | VPS Ubuntu (4 meses × S/.40) | 160.00 |
| | Dominio web (.com, 1 año) | 50.00 |
| | SSL (Let's Encrypt) | 0.00 |
| | **Subtotal** | **210.00** |
| **Costos de Personal** | | |
| | JLM – Backend/ETL (12h/sem × 16 sem × S/.15) | 2,880.00 |
| | UHR – Frontend/Auth (12h/sem × 16 sem × S/.15) | 2,880.00 |
| | **Subtotal** | **5,760.00** |
| **TOTAL GENERAL** | | **6,590.00** |

<span id="factibilidad-pp"></span>
### 3. Análisis de Factibilidad

El análisis completo se encuentra en el documento FD01 (Informe de Factibilidad). Resumen:

- **Factibilidad Técnica**: ✅ Tecnologías maduras y de código abierto.
- **Factibilidad Económica**: ✅ Costo accesible (S/. 6,590.00).
- **Factibilidad Operativa**: ✅ Equipo competente, interfaz intuitiva.
- **Factibilidad Legal**: ✅ Sin conflictos, licencias permisivas.
- **Factibilidad Social**: ✅ Democratiza acceso a herramientas de migración.
- **Factibilidad Ambiental**: ✅ Impacto mínimo, sistema web sin distribución física.

<span id="evaluacion-financiera"></span>
### 4. Evaluación Financiera

| Indicador | Valor | Resultado |
|:----------|:------|:---------|
| Relación Beneficio/Costo (B/C) | 1.21 | Se acepta (B/C > 1) |
| Valor Actual Neto (VAN) | S/. 13,304.82 | Se acepta (VAN > 0) |
| Tasa Interna de Retorno (TIR) | 112% | Se acepta (TIR > COK 10%) |

---

<span id="anexo-requerimientos"></span>
## Anexo 01 – Requerimientos del Sistema MigradorBD

### Requerimientos Funcionales Principales

| ID | Requerimiento | Módulo | Estado |
|:---|:-------------|:-------|:-------|
| RF-01 | Subir archivos de BD (hasta 500 MB) | app/routes.py | ✅ Implementado |
| RF-02 | Detección automática del motor de origen | utilidades/detector.py | ✅ Implementado |
| RF-03 | Extracción de esquema y datos | extraccion/conector.py | ✅ Implementado |
| RF-04 | Generación de exportaciones multi-formato | carga/cargador.py | ✅ Implementado |
| RF-05 | Autenticación local con verificación email | app/auth.py | ✅ Implementado |
| RF-06 | OAuth con Google y GitHub | app/oauth.py | ✅ Implementado |
| RF-07 | Progreso en tiempo real (WebSocket) | app/routes.py + SocketIO | ✅ Implementado |
| RF-08 | Integración con GitHub (repos + upload) | app/routes.py | ✅ Implementado |
| RF-09 | Historial de migraciones | app/routes.py | ✅ Implementado |
| RF-10 | Panel de administración | app/routes.py + auth.py | ✅ Implementado |

### Requerimientos No Funcionales

| ID | Requerimiento | Estado |
|:---|:-------------|:-------|
| RNF-01 | Rendimiento: 50 MB en < 60s | ✅ Cumplido |
| RNF-02 | Seguridad: hash scrypt + HttpOnly cookies | ✅ Cumplido |
| RNF-03 | Portabilidad: Windows + Linux | ✅ Cumplido |
| RNF-04 | Aislamiento de archivos por usuario | ✅ Cumplido |
| RNF-05 | Errores en formato JSON | ✅ Cumplido |
