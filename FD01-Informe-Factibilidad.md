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

Sistema *MigradorBD*

Informe de Factibilidad

Versión *1.0*

|CONTROL DE VERSIONES||||||
| :-: | :- | :- | :- | :- | :- |
|Versión|Hecha por|Revisada por|Aprobada por|Fecha|Motivo|
|1\.0|JLM / UHR|JLM|UHR|06/06/2026|Versión Original|

<div style="page-break-after: always; visibility: hidden">\pagebreak</div>

# **INDICE GENERAL**

[1. Descripción del Proyecto](#_Toc52661346)

[2. Riesgos](#_Toc52661347)

[3. Análisis de la Situación actual](#_Toc52661348)

[4. Estudio de Factibilidad](#_Toc52661349)

[4.1 Factibilidad Técnica](#_Toc52661350)

[4.2 Factibilidad económica](#_Toc52661351)

[4.3 Factibilidad Operativa](#_Toc52661352)

[4.4 Factibilidad Legal](#_Toc52661353)

[4.5 Factibilidad Social](#_Toc52661354)

[4.6 Factibilidad Ambiental](#_Toc52661355)

[5. Análisis Financiero](#_Toc52661356)

[6. Conclusiones](#_Toc52661357)


<div style="page-break-after: always; visibility: hidden">\pagebreak</div>

**<u>Informe de Factibilidad</u>**

1. <span id="_Toc52661346" class="anchor"></span>**Descripción del Proyecto**

    1.1. Nombre del proyecto

        MigradorBD – Sistema Integral de Migración de Bases de Datos

    1.2. Duración del proyecto

        El proyecto tiene una duración estimada de 4 meses (marzo – junio 2026), correspondiente al ciclo académico 2026-I.

    1.3. Descripción

        MigradorBD es un sistema web integral que permite la migración de datos entre múltiples motores de bases de datos mediante un proceso ETL (Extracción, Transformación y Carga). El sistema soporta la migración entre motores relacionales (MySQL, PostgreSQL, Microsoft SQL Server, Oracle, SQLite), motores NoSQL (MongoDB, Elasticsearch, Apache Cassandra, Redis) y formatos de archivo (CSV, Excel, JSON). Adicionalmente, el sistema incluye autenticación segura con soporte OAuth (Google y GitHub), control de roles (administrador/usuario), integración directa con repositorios de GitHub para almacenamiento de exportaciones, detección automática del tipo de base de datos a partir del contenido del archivo, interfaz web interactiva con comunicación en tiempo real vía WebSocket y soporte para despliegue en producción con Nginx y Gunicorn.

        La importancia del proyecto radica en la necesidad de las organizaciones de migrar datos entre diferentes sistemas de gestión de bases de datos de manera eficiente, segura y sin pérdida de información. Actualmente, la migración entre motores heterogéneos es un proceso complejo que requiere conocimientos especializados y herramientas costosas.

    1.4. Objetivos

        1.4.1 Objetivo general

        Desarrollar un sistema web de migración de bases de datos que permita la extracción, transformación y carga de datos entre múltiples motores de bases de datos de forma automatizada, segura y eficiente.

        1.4.2 Objetivos Específicos

        - Implementar un módulo de extracción capaz de conectar y leer datos desde archivos SQLite, scripts SQL (MySQL, PostgreSQL, SQL Server, Oracle), JSON, CSV y Excel.
        - Desarrollar un módulo de transformación que adapte los datos al esquema del motor destino, incluyendo limpieza de datos y mapeo de tipos.
        - Construir un módulo de carga que genere exportaciones compatibles con más de 15 motores de bases de datos destino, incluyendo formatos SQL, JSON, NDJSON, CQL y comandos Redis.
        - Implementar un sistema de detección automática del tipo de base de datos basado en análisis de contenido del archivo.
        - Integrar autenticación segura con soporte para registro local, verificación por email y OAuth con Google y GitHub.
        - Desarrollar una interfaz web interactiva con actualizaciones en tiempo real mediante WebSocket.
        - Implementar integración con GitHub para almacenamiento y versionamiento de las exportaciones.

<div style="page-break-after: always; visibility: hidden">\pagebreak</div>

2. <span id="_Toc52661347" class="anchor"></span>**Riesgos**

    Los principales riesgos identificados para el proyecto son:

    | N° | Riesgo | Probabilidad | Impacto | Mitigación |
    |:---|:-------|:-------------|:--------|:-----------|
    | 1 | Incompatibilidad de tipos de datos entre motores SQL heterogéneos | Alta | Alto | Implementar un mapeador de tipos (`_tipo_sql_destino`) con soporte para cada motor destino |
    | 2 | Archivos SQL con sintaxis no estándar o corrupta | Media | Medio | Análisis robusto con expresiones regulares tolerantes a errores y fallback a tipo genérico |
    | 3 | Pérdida de datos durante la transformación | Media | Alto | Validación post-carga y registro detallado de métricas (extraídos, cargados, errores) |
    | 4 | Problemas de rendimiento con archivos grandes (>100MB) | Media | Medio | Procesamiento por lotes configurables (batch de 1000 para extracción, 500 para carga) |
    | 5 | Fallas en la autenticación OAuth por configuración incorrecta | Baja | Medio | Documentación detallada de configuración y variables de entorno |
    | 6 | Vulnerabilidades de seguridad en el manejo de credenciales | Baja | Alto | Uso de hashing con Werkzeug/scrypt, cookies seguras y sesiones HTTPOnly |

<div style="page-break-after: always; visibility: hidden">\pagebreak</div>

3. <span id="_Toc52661348" class="anchor"></span>**Análisis de la Situación actual**

    3.1. Planteamiento del problema

        En el entorno actual de desarrollo de software y administración de sistemas, las organizaciones frecuentemente necesitan migrar datos entre diferentes motores de bases de datos. Esta necesidad surge por diversas razones: actualización de tecnología, consolidación de sistemas, migración a la nube, cambio de proveedor de base de datos, o integración entre sistemas heterogéneos.

        Actualmente, los procesos de migración entre bases de datos presentan las siguientes problemáticas:
        
        - **Complejidad técnica**: Cada motor tiene su propia sintaxis SQL, tipos de datos y características específicas. La traducción entre motores requiere conocimiento especializado.
        - **Costo elevado**: Las herramientas comerciales de migración (como AWS Database Migration Service, Oracle Data Pump, o Microsoft SSMA) tienen costos de licenciamiento significativos.
        - **Proceso manual propenso a errores**: La migración manual mediante scripts ad-hoc es lenta, propensa a errores y difícil de replicar.
        - **Falta de soporte multi-motor**: La mayoría de herramientas solo soportan migración entre 2-3 motores específicos, no entre ecosistemas completos.
        - **Sin detección automática**: El usuario debe conocer de antemano el tipo y formato del archivo de origen.

    3.2. Consideraciones de hardware y software

        **Hardware requerido:**
        - Servidor o equipo con mínimo 4 GB de RAM
        - 10 GB de almacenamiento disponible para archivos temporales de migración
        - Conexión a internet para funcionalidades OAuth y GitHub

        **Software requerido:**
        - Python 3.12+ como lenguaje de desarrollo
        - Flask 2.3.3 como framework web
        - SQLAlchemy 2.0.23 para abstracción de bases de datos
        - Flask-SocketIO 5.3.0 para comunicación en tiempo real
        - Authlib 1.2.0 para OAuth
        - Pandas 2.1.1 para manipulación de datos
        - Gunicorn 21.2.0 para servidor de producción
        - Nginx como proxy reverso en producción

<div style="page-break-after: always; visibility: hidden">\pagebreak</div>

4. <span id="_Toc52661349" class="anchor"></span>**Estudio de
    Factibilidad**

    El estudio de factibilidad se realizó evaluando las dimensiones técnica, económica, operativa, legal, social y ambiental del proyecto MigradorBD. Los resultados demuestran que el proyecto es viable en todas las dimensiones evaluadas.

    4.1. <span id="_Toc52661350" class="anchor"></span>Factibilidad Técnica

        El proyecto es técnicamente factible dado que utiliza tecnologías maduras y ampliamente documentadas:

        **Lenguaje de programación:**
        - Python 3.12: Lenguaje de alto nivel con amplio ecosistema para manejo de datos y desarrollo web.

        **Framework web:**
        - Flask 2.3.3: Microframework web ligero y flexible.
        - Flask-SocketIO 5.3.0: Extensión para WebSocket con soporte para comunicación bidireccional en tiempo real.

        **Base de datos intermedia:**
        - SQLite: Base de datos embebida para almacenamiento temporal durante el proceso ETL.
        - SQLAlchemy 2.0.23: ORM para abstracción de acceso a datos.

        **Bibliotecas de procesamiento:**
        - Pandas 2.1.1: Manipulación y transformación de datos tabulares.
        - NumPy 1.26.4: Operaciones numéricas de soporte.
        - OpenPyXL 3.1.3: Lectura/escritura de archivos Excel.

        **Autenticación y seguridad:**
        - Authlib 1.2.0: Implementación de OAuth 2.0 para Google y GitHub.
        - Werkzeug 2.3.7: Hashing seguro de contraseñas con scrypt.
        - Bcrypt 4.0.1: Algoritmo de hashing adicional.

        **Infraestructura de producción:**
        - Gunicorn 21.2.0: Servidor WSGI para producción.
        - Eventlet 0.33.3: Servidor asíncrono para WebSocket.
        - Nginx: Proxy reverso y servidor de archivos estáticos.
        - Supervisor: Gestión de procesos en producción.

        Todos los componentes son de código abierto y están disponibles gratuitamente.

    4.2. <span id="_Toc52661351" class="anchor"></span>Factibilidad Económica

        4.2.1. Costos Generales

        | Descripción | Cantidad | Costo Unitario (S/.) | Costo Total (S/.) |
        |:------------|:---------|:---------------------|:-------------------|
        | Papel bond A4 | 1 millar | 25.00 | 25.00 |
        | USB 32GB | 2 | 30.00 | 60.00 |
        | Útiles de escritorio | 1 set | 15.00 | 15.00 |
        | **Total** | | | **100.00** |

        4.2.2. Costos operativos durante el desarrollo

        | Descripción | Costo Mensual (S/.) | Meses | Costo Total (S/.) |
        |:------------|:--------------------|:------|:-------------------|
        | Servicio de Internet | 80.00 | 4 | 320.00 |
        | Energía eléctrica | 50.00 | 4 | 200.00 |
        | **Total** | | | **520.00** |

        4.2.3. Costos del ambiente

        | Descripción | Costo Mensual (S/.) | Meses | Costo Total (S/.) |
        |:------------|:--------------------|:------|:-------------------|
        | VPS Ubuntu (2 CPU, 4GB RAM) | 40.00 | 4 | 160.00 |
        | Dominio web (.com) | 50.00 | 1 (anual) | 50.00 |
        | Certificado SSL (Let's Encrypt) | 0.00 | - | 0.00 |
        | **Total** | | | **210.00** |

        4.2.4. Costos de personal

        | Rol | Integrante | Horas/Semana | Semanas | Costo/Hora (S/.) | Costo Total (S/.) |
        |:----|:-----------|:-------------|:--------|:------------------|:-------------------|
        | Desarrollador Backend/ETL | LLica Mamani, Jimmy Mijair | 12 | 16 | 15.00 | 2,880.00 |
        | Desarrollador Frontend/Auth | Halanocca Rojas, Usher Damiron | 12 | 16 | 15.00 | 2,880.00 |
        | **Total** | | | | | **5,760.00** |

        4.2.5. Costos totales del desarrollo del sistema

        | Concepto | Costo (S/.) |
        |:---------|:------------|
        | Costos Generales | 100.00 |
        | Costos Operativos | 520.00 |
        | Costos del Ambiente | 210.00 |
        | Costos de Personal | 5,760.00 |
        | **TOTAL** | **6,590.00** |

    4.3. <span id="_Toc52661352" class="anchor"></span>Factibilidad Operativa

        El sistema MigradorBD es operativamente factible debido a:

        - **Interfaz intuitiva**: La aplicación web presenta una interfaz paso a paso que guía al usuario en el proceso de migración (subir archivo → seleccionar destino → ejecutar migración → descargar resultado).
        - **Detección automática**: El sistema detecta automáticamente el tipo de base de datos del archivo subido, eliminando la necesidad de que el usuario tenga conocimiento técnico sobre el formato del archivo.
        - **Actualizaciones en tiempo real**: El uso de WebSocket permite que el usuario observe el progreso de la migración en tiempo real.
        - **Documentación completa**: El proyecto incluye documentación técnica detallada para despliegue, configuración de OAuth, y guías de inicio rápido.
        - **Capacidad del equipo**: Los integrantes del equipo poseen las competencias necesarias en Python, Flask, bases de datos y desarrollo web.

        **Lista de interesados:**
        - Administradores de bases de datos
        - Desarrolladores de software
        - Empresas que requieren migración de datos
        - Docentes y estudiantes de ingeniería de sistemas

    4.4. <span id="_Toc52661353" class="anchor"></span>Factibilidad Legal

        El proyecto no presenta conflictos legales dado que:

        - Todas las tecnologías utilizadas son de código abierto con licencias permisivas (MIT, BSD, Apache 2.0).
        - El sistema no almacena datos sensibles de terceros; los archivos subidos son procesados y el usuario descarga el resultado.
        - La implementación de OAuth cumple con los estándares de autenticación de Google y GitHub.
        - El sistema cumple con la Ley N° 29733 (Ley de Protección de Datos Personales del Perú) al implementar cookies seguras, sesiones con HTTPOnly y SameSite, y hashing de contraseñas.

    4.5. <span id="_Toc52661354" class="anchor"></span>Factibilidad Social

        El proyecto tiene un impacto social positivo al:

        - Democratizar el acceso a herramientas de migración de bases de datos, ofreciendo una alternativa gratuita y de código abierto a soluciones comerciales costosas.
        - Facilitar el aprendizaje sobre procesos ETL y arquitectura de bases de datos para estudiantes de ingeniería.
        - Promover buenas prácticas de desarrollo de software mediante código documentado y estructurado.

    4.6. <span id="_Toc52661355" class="anchor"></span>Factibilidad Ambiental

        El impacto ambiental del proyecto es mínimo:

        - Al ser un sistema web, no requiere distribución física de software.
        - El uso de VPS compartido minimiza el consumo energético comparado con infraestructura dedicada.
        - La migración automatizada reduce el tiempo de proceso y, por tanto, el consumo de recursos computacionales comparado con procesos manuales.

<div style="page-break-after: always; visibility: hidden">\pagebreak</div>

5. <span id="_Toc52661356" class="anchor"></span>**Análisis Financiero**

    5.1. Justificación de la Inversión

        5.1.1. Beneficios del Proyecto

            **Beneficios tangibles:**
            - Reducción del tiempo de migración de bases de datos de días/semanas a minutos/horas.
            - Eliminación del costo de licencias de herramientas comerciales de migración (estimado en $500 - $5,000 USD anuales por herramienta).
            - Reducción de errores humanos en el proceso de migración en un estimado del 80%.
            - Soporte para más de 15 motores de bases de datos destino en una sola herramienta.

            **Beneficios intangibles:**
            - Mejora en la eficiencia operativa del equipo de desarrollo/DBA.
            - Disponibilidad de información migrada de forma oportuna y precisa.
            - Mejora en la toma de decisiones al facilitar la consolidación de datos.
            - Ventaja competitiva al ofrecer una solución multi-motor sin precedentes.
            - Aumento en la confiabilidad del proceso de migración al ser automatizado y auditable.

        5.1.2. Criterios de Inversión

            5.1.2.1. Relación Beneficio/Costo (B/C)

                Considerando un ahorro anual estimado de S/. 8,000.00 (por eliminación de licencias y reducción de horas-hombre en migraciones manuales) frente a un costo total de desarrollo de S/. 6,590.00:

                B/C = 8,000.00 / 6,590.00 = **1.21**

                Al ser B/C > 1, el proyecto se acepta.

            5.1.2.2. Valor Actual Neto (VAN)

                Con una tasa de descuento del 10% y un horizonte de 3 años:

                VAN = -6,590 + (8,000/1.10) + (8,000/1.21) + (8,000/1.331)
                VAN = -6,590 + 7,272.73 + 6,611.57 + 6,010.52
                VAN = **S/. 13,304.82**

                Al ser VAN > 0, el proyecto se acepta.

            5.1.2.3 Tasa Interna de Retorno (TIR)

                La TIR calculada para el proyecto es de aproximadamente **112%**, lo cual es significativamente mayor que el costo de oportunidad del capital (10%).

                Al ser TIR > COK, el proyecto se acepta.

<div style="page-break-after: always; visibility: hidden">\pagebreak</div>

6. <span id="_Toc52661357" class="anchor"></span>**Conclusiones**

    El análisis de factibilidad del proyecto MigradorBD demuestra que el sistema es viable en todas las dimensiones evaluadas:

    - **Técnicamente factible**: Se dispone de todas las tecnologías necesarias (Python, Flask, SQLAlchemy, Pandas), todas de código abierto y ampliamente documentadas.
    - **Económicamente factible**: El costo total de S/. 6,590.00 es accesible y los indicadores financieros (B/C = 1.21, VAN = S/. 13,304.82, TIR = 112%) confirman la rentabilidad del proyecto.
    - **Operativamente factible**: El equipo de desarrollo tiene las competencias necesarias y el sistema está diseñado para ser intuitivo y autoexplicativo.
    - **Legalmente factible**: No existen conflictos con regulaciones legales y se cumplen las normas de protección de datos.
    - **Social y ambientalmente responsable**: El proyecto democratiza el acceso a herramientas de migración y tiene un impacto ambiental mínimo.

    En consecuencia, se recomienda proceder con el desarrollo e implementación del sistema MigradorBD.
