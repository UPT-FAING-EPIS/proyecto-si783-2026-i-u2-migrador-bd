# 🔄 MigradorBD

Sistema integral de migración de bases de datos que permite la extracción, transformación y carga (ETL) entre múltiples motores, incluyendo autenticación segura, control de roles y conexión con GitHub.

---

## 📁 Estructura del Proyecto Organizada

El proyecto ha sido restructurado para mantener el directorio raíz ordenado. Los archivos están agrupados de la siguiente forma:

* **[app/](file:///c:/proyecto-si783-2026-i-u2-migrador-bd/proyecto-si783-2026-i-u1-migrador-de-bd-codigo-web/app)**: Código fuente de la aplicación Flask (rutas, plantillas HTML, recursos estáticos, lógica de autenticación y WebSocket).
* **[despliegue/](file:///c:/proyecto-si783-2026-i-u2-migrador-bd/proyecto-si783-2026-i-u1-migrador-de-bd-codigo-web/despliegue)**: Contiene los scripts de automatización e instalación de servidores, configuraciones de Nginx, Supervisor y Systemd para la puesta en producción en el VPS.
* **[docs/](file:///c:/proyecto-si783-2026-i-u2-migrador-bd/proyecto-si783-2026-i-u1-migrador-de-bd-codigo-web/docs)**: Guías y manuales de configuración detallados.
* **[tests/](file:///c:/proyecto-si783-2026-i-u2-migrador-bd/proyecto-si783-2026-i-u1-migrador-de-bd-codigo-web/tests)**: Archivos de prueba y scripts de testeo para la detección de motores y bases de datos.
* **Módulos del Motor ETL**:
  * **[extraccion/](file:///c:/proyecto-si783-2026-i-u2-migrador-bd/proyecto-si783-2026-i-u1-migrador-de-bd-codigo-web/extraccion)**: Conectores y extractores de origen.
  * **[transformacion/](file:///c:/proyecto-si783-2026-i-u2-migrador-bd/proyecto-si783-2026-i-u1-migrador-de-bd-codigo-web/transformacion)**: Mapeadores y traductores de datos.
  * **[carga/](file:///c:/proyecto-si783-2026-i-u2-migrador-bd/proyecto-si783-2026-i-u1-migrador-de-bd-codigo-web/carga)**: Cargadores y constructores de destino.
  * **[utilidades/](file:///c:/proyecto-si783-2026-i-u2-migrador-bd/proyecto-si783-2026-i-u1-migrador-de-bd-codigo-web/utilidades)**: Herramientas del sistema y detector automático de motores.

---

## 📚 Índice de Documentación (`docs/`)

Para configurar o desplegar la aplicación, consulta las siguientes guías específicas dentro de la carpeta `docs/`:

* **Autenticación y OAuth:**
  * [Configuración de Google y GitHub OAuth](docs/OAUTH_SETUP.md) ➜ Guía para obtener Client IDs/Secrets y configurar redirecciones.
  * [Sistema de Autenticación Completo](docs/README_AUTH.md) ➜ Detalle técnico sobre sesiones, contraseñas y base de datos de usuarios.
  * [Documentación de Flujos de Autenticación](docs/AUTENTICACION.md) ➜ Esquemas de flujo de usuario y roles.

* **Guías de Despliegue en Producción (VPS/Ubuntu):**
  * [Guía de Despliegue Completo en Ubuntu](docs/DEPLOY_UBUNTU.md) ➜ Pasos paso a paso detallados para configurar Nginx, SSL y servicios.
  * [Resumen Visual y Referencia de Despliegue](docs/DEPLOYMENT_SUMMARY.md) ➜ Lista de puertos, comandos rápidos y checklist.
  * [Despliegue Directo Sin Dominio (Solo con IP)](docs/SIN_DOMINIO.md) ➜ Cómo levantar la app si no tienes un dominio adquirido.
  * [Manual de Despliegue con IP VPS](docs/DEPLOY_CON_IP.md) ➜ Referencia rápida de comandos para IPs estáticas.
  * [Guía de Inicio Rápido](docs/QUICK_START.md) ➜ Primeros pasos para levantar el entorno localmente o en VPS.
  * [Referencia de Arranque de Producción](docs/README_DESPLIEGUE.md) ➜ Comandos rápidos para inicializar.

---

## 🛠️ Desarrollo Local

1. Instala las dependencias:
   ```bash
   pip install -r requirements.txt
   ```
2. Configura tu archivo `.env` tomando como base el archivo `.env.example`.
3. Inicia el servidor de desarrollo:
   ```bash
   python run.py
   ```
