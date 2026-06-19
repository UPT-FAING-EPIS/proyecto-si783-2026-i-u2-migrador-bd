# Documentación Oficial - Migrador DB Enterprise Enterprise

Bienvenidos al repositorio de documentación del proyecto **Migrador DB Enterprise - Sistema Integral de Migración de Bases de Datos**.

Este directorio contiene toda la documentación formal, técnica, arquitectónica y de gestión (Formatos FD) del proyecto, desarrollada rigurosamente de acuerdo con los estándares y lineamientos del curso de **Ingeniería de Software (SI783)** de la **Universidad Privada de Tacna (2026)**.

## 📖 Índice y Descripción de Documentos

El proyecto cuenta con una amplia documentación estructurada en 6 formatos principales (FD). A continuación se detalla el contenido y propósito de cada uno:

### 1. [FD01 - Informe de Factibilidad](./FD01-Informe-Factibilidad.md)
Este documento presenta el estudio exhaustivo de viabilidad del proyecto, asegurando que su ejecución es posible desde todos los ángulos estratégicos:
*   **Factibilidad Técnica:** Análisis de la pila tecnológica seleccionada (Python 3.12+, Flask, SQLAlchemy, Pandas, Authlib, Gunicorn, SocketIO).
*   **Factibilidad Económica:** Desglose del presupuesto de inversión (S/. 6,590.00), cálculo de Retorno de Inversión (VAN, TIR) y relación Beneficio/Costo.
*   **Factibilidad Operativa, Legal, Social y Ambiental:** Evaluación del impacto del sistema en el entorno y cumplimiento de la Ley de Protección de Datos Personales (Ley N° 29733).
*   **Gestión de Riesgos:** Matriz de riesgos identificando posibles bloqueos en la migración (ej. incompatibilidad de tipos SQL) y sus planes de mitigación.

### 2. [FD02 - Informe de Visión](./FD02-Informe-Vision.md)
Establece la dirección estratégica del producto y su posicionamiento frente a alternativas comerciales:
*   **Oportunidad de Negocio:** Posicionamiento como una herramienta de código abierto que compite con soluciones costosas como AWS DMS o Azure Database Migration Service.
*   **Perfiles de Interesados y Usuarios:** Definición clara de las responsabilidades del equipo de desarrollo, administradores de bases de datos y usuarios finales.
*   **Características Principales:** Describe las capacidades clave como la detección automática del motor, el pipeline ETL, la autenticación OAuth, y la monitorización vía WebSocket.

### 3. [FD03 - Especificación de Requerimientos de Software (SRS)](./FD03-EPIS-Informe%20Especificaci%C3%B3n%20Requerimientos.md)
Catálogo completo y detallado de todo lo que el sistema debe hacer y cómo debe comportarse:
*   **Requerimientos Funcionales (24 RF):** Detalla capacidades de carga de archivos (hasta 500 MB), extracción de esquemas, soporte para 15+ motores destino, autenticación y despliegue.
*   **Requerimientos No Funcionales (10 RNF):** Establece las métricas de rendimiento (archivos de 50MB en < 60s), seguridad (hash scrypt, HttpOnly cookies), y portabilidad (Windows y Linux).
*   **Modelado y Casos de Uso:** Incluye el modelo relacional de la base de datos de autenticación (tablas `usuarios` y `oauth_usuarios`) y los flujos de negocio.

### 4. [FD04 - Informe de Arquitectura de Software (SAD)](./FD04-EPIS-Informe%20Arquitectura%20de%20Software.md)
Documento técnico estructurado bajo el modelo **4+1 Vistas de Philippe Kruchten**, esencial para desarrolladores:
*   **Vista Lógica:** Diagramas de paquetes y clases base (`ConectorOrigen`, `MapeadorDatos`, `CargadorDestino`, `DetectorBaseDatos`).
*   **Vista de Implementación:** Organización del código fuente en capas bien definidas (Presentación, Aplicación, ETL y Datos).
*   **Vista de Procesos:** Algoritmos heurísticos de detección y pipeline de transformación por bloques (Chunking).
*   **Vista de Despliegue:** Topología de producción para servidores Ubuntu utilizando Nginx como proxy inverso, Supervisor y Gunicorn.

### 5. [FD05 - Informe de Proyecto Final](./FD05-EPIS-Informe%20ProyectoFinal.md)
Documento de cierre que resume la ejecución y el cumplimiento de los objetivos planteados:
*   **Metodología de Desarrollo:** Aplicación de metodologías ágiles dividida en 4 iteraciones de desarrollo a lo largo de 16 semanas.
*   **Conclusiones Finales:** Evaluación del éxito en el parseo de esquemas complejos y la preservación de objetos SQL avanzados (Triggers, Procedimientos, Vistas).
*   **Recomendaciones para Trabajo Futuro:** Propuestas de escalabilidad técnica, como la integración de Celery y Redis para procesamiento asíncrono en segundo plano, y soporte para conexiones de bases de datos remotas.

### 6. [FD06 - Propuesta de Proyecto](./FD06-EPIS-PropuestaProyecto.md)
El documento inicial que dio luz verde al proyecto:
*   **Planteamiento del Problema:** Análisis profundo sobre los cuellos de botella en las migraciones manuales.
*   **Resultados Esperados y Hitos:** Cronograma inicial y matriz de responsables.

---

## 🏗️ Relación con el Código Fuente

Toda esta documentación respalda el código que se encuentra alojado en la carpeta `proyecto-si783-2026-i-u1-migrador-de-bd-codigo-web`. La arquitectura descrita en el **FD04** se refleja directamente en la siguiente estructura modular del proyecto:

*   📂 **`app/`**: Contiene la lógica del framework Flask, rutas, plantillas web, y seguridad.
*   📂 **`extraccion/`**: Módulos responsables de leer los archivos SQL, SQLite, JSON, CSV o Excel y extraer tanto el esquema como la data.
*   📂 **`transformacion/`**: Lógica de conversión de tipos de datos para que sean compatibles entre motores (e.g. `VARCHAR2` de Oracle a `TEXT` de PostgreSQL).
*   📂 **`carga/`**: Subsistema final que inyecta la información formateada (`.sql`, `.json`, `.cql`, `.ndjson`, comandos redis).
*   📂 **`utilidades/`**: Módulo inteligente `detector.py` para adivinar automáticamente de qué motor proviene el archivo subido usando análisis de expresiones regulares.

---

## 👥 Equipo Responsable

**Universidad Privada de Tacna**  
**Facultad de Ingeniería - Escuela Profesional de Ingeniería de Sistemas**

*   👨‍💻 **LLica Mamani, Jimmy Mijair** - *Desarrollador Backend / Especialista ETL*
*   👨‍💻 **Halanocca Rojas, Usher Damiron** - *Desarrollador Frontend / Especialista Seguridad Auth*

*Tacna, Perú - 2026*