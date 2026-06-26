# Guía de Uso del Migrador de Base de Datos

Este proyecto cuenta con dos integraciones principales para facilitar la migración de bases de datos. A continuación, te explicamos paso a paso cómo utilizar cada una de ellas.

---

## 1. Uso mediante la Inteligencia Artificial (Agent Skill)

Esta integración está diseñada para que interactúes directamente con cualquier Agente de Inteligencia Artificial (como Antigravity, GitHub Copilot, Cursor, etc.) dentro de tu editor de código. El archivo `SKILL.md` es el manual de instrucciones del agente, por lo que tú no necesitas leerlo, solo darle la orden.

**Paso a paso:**

1. **Abre tu IDE** y asegúrate de tener este proyecto abierto.
2. **Abre el chat del Agente de IA** que estés utilizando.
3. **Pide al agente que realice una migración** usando lenguaje natural. No necesitas conocer los comandos complejos.
   * **Ejemplo 1:** *"Migra el archivo dummy_source.sql a formato postgres. El archivo resultante debe llamarse migracion_db."*
   * **Ejemplo 2:** *"Utiliza la skill migrador-bd para convertir mi base de datos test.sqlite actual a MySQL y ponlo en la carpeta output."*
4. **Espera a que la IA actúe:**
   * Yo leeré automáticamente las instrucciones de la skill.
   * Ejecutaré el entorno virtual y los comandos de Python en tu terminal por ti.
5. **Revisa los resultados:** Te informaré sobre el éxito de la migración y los archivos generados aparecerán en tu espacio de trabajo.

---

## 2. Uso mediante GitHub Actions (En la Nube)

Esta integración está pensada para que cualquier miembro del equipo (incluso sin conocimientos de programación) pueda realizar migraciones desde la web de GitHub, sin instalar Python en su computadora.

**Paso a paso:**

1. **Entra al repositorio** del proyecto en la página web de GitHub.
2. **Ve a la pestaña "Actions"** (Acciones) ubicada en la parte superior, debajo del nombre del repositorio.
3. **Selecciona el flujo de trabajo (Workflow):** En la barra lateral izquierda, haz clic en **"Ejecutar Migración de BD"**.
4. **Inicia la ejecución:** Haz clic en el botón desplegable de la derecha que dice **"Run workflow"** (Ejecutar flujo de trabajo).
5. **Llena el formulario con los parámetros:**
   * **Archivo de origen:** Escribe el nombre del archivo que quieres migrar (Ej: `test.sqlite`). *(Nota: el archivo debe existir dentro del repositorio)*.
   * **Nombre para el archivo migrado:** Escribe cómo quieres que se llame el resultado (Ej: `mi_migracion_final`).
   * **Formato de destino:** Selecciona a qué motor de base de datos quieres migrar usando el menú desplegable (Ej: `mysql`, `postgres`, `mongodb`, etc.).
6. **Ejecutar:** Haz clic en el botón verde **"Run workflow"**.
7. **Espera el proceso:** Verás que aparece una nueva ejecución (un círculo amarillo que luego cambia a un check verde). Puedes hacer clic en ella para ver cómo avanza el proceso.
8. **Descarga el resultado:** Cuando el proceso termine exitosamente, ábrelo y desplázate hacia abajo. En la sección de **"Artifacts"** (Artefactos), verás un archivo llamado `archivo-migrado`. Haz clic en él para descargar los resultados comprimidos en tu computadora.
