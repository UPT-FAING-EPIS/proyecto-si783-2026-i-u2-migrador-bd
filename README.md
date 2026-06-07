# Migrador DB Enterprise

Acceso a la plataforma oficial: [https://migradordb.online/](https://migradordb.online/)

Sistema integral de migración de bases de datos de nivel corporativo. Permite la extracción, transformación y carga (ETL) de estructuras complejas (tablas, vistas, triggers y procedimientos almacenados) entre múltiples motores de bases de datos mediante un algoritmo eficiente de procesamiento por bloques (Chunking RAM).

---

## Estructura del Proyecto

El código fuente está estructurado en módulos para garantizar la escalabilidad técnica:

* **[app/](file:///c:/proyecto-si783-2026-i-u2-migrador-bd/proyecto-si783-2026-i-u1-migrador-de-bd-codigo-web/app)**: Lógica principal de la aplicación web (Rutas Flask, plantillas, autenticación, foro de comunidad y sockets).
* **[despliegue/](file:///c:/proyecto-si783-2026-i-u2-migrador-bd/proyecto-si783-2026-i-u1-migrador-de-bd-codigo-web/despliegue)**: Automatización de infraestructura (Nginx, Supervisor, Systemd).
* **[docs/](file:///c:/proyecto-si783-2026-i-u2-migrador-bd/proyecto-si783-2026-i-u1-migrador-de-bd-codigo-web/docs)**: Documentación técnica y arquitectura de la plataforma.
* **[tests/](file:///c:/proyecto-si783-2026-i-u2-migrador-bd/proyecto-si783-2026-i-u1-migrador-de-bd-codigo-web/tests)**: Pruebas unitarias de conexión e integración de bases de datos.

### Módulos del Motor ETL

* **[extraccion/](file:///c:/proyecto-si783-2026-i-u2-migrador-bd/proyecto-si783-2026-i-u1-migrador-de-bd-codigo-web/extraccion)**: Conectores y extractores de origen.
* **[transformacion/](file:///c:/proyecto-si783-2026-i-u2-migrador-bd/proyecto-si783-2026-i-u1-migrador-de-bd-codigo-web/transformacion)**: Analizadores sintácticos y conversores de tipos.
* **[carga/](file:///c:/proyecto-si783-2026-i-u2-migrador-bd/proyecto-si783-2026-i-u1-migrador-de-bd-codigo-web/carga)**: Inserción optimizada en motores de destino.
* **[utilidades/](file:///c:/proyecto-si783-2026-i-u2-migrador-bd/proyecto-si783-2026-i-u1-migrador-de-bd-codigo-web/utilidades)**: Detección automática de dialectos y funciones de soporte.

---

## Documentación Técnica

Consulte el directorio `docs/` para guías detalladas de implementación:

* **Seguridad y Autenticación**
  * Configuración de proveedores OAuth (Google/GitHub).
  * Documentación de flujos de autenticación y control de roles de usuario.

* **Despliegue en Producción**
  * Guía de despliegue completo en servidores Ubuntu (Linux).
  * Resumen de puertos, configuración SSL y monitorización de procesos.

---

## Entorno de Desarrollo Local

1. Instalación de dependencias:
   ```bash
   pip install -r requirements.txt
   ```

2. Configuración de variables de entorno:
   Copie `.env.example` a `.env` y ajuste los parámetros requeridos.

3. Ejecución del servidor web:
   ```bash
   python run.py
   ```
