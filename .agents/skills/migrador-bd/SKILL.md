---
name: migrador-bd
description: Realiza migraciones automatizadas de bases de datos utilizando los componentes del proyecto (extractor, mapeador, cargador).
---

# Skill: Migrador de Bases de Datos

Esta skill permite ejecutar el sistema de migración de bases de datos de forma programática.

## Capacidades

Cuando el usuario te pida "ejecutar una migración", "migrar la base de datos", o algo similar:

1. **Obtener parámetros:**
   Pregunta al usuario (si no lo especificó) por los siguientes datos:
   - Origen (tipo de BD y conexión/ruta)
   - Destino (tipo de BD y conexión/ruta)
   - Tablas a migrar (o si es migración completa)

2. **Ejecución:**
   Debes ejecutar el script auxiliar para realizar la migración real. Este script importa la lógica subyacente.
   Comando de ejemplo:
   ```bash
   python .agents/skills/migrador-bd/scripts/cli_migrator.py --source <ruta_origen> --dest <ruta_destino> --tipo-origen <sqlite|mysql|postgres> --tipo-dest <sqlite|mysql|postgres>
   ```

3. **Verificación:**
   Una vez que el script finaliza, reporta el resultado al usuario, incluyendo la cantidad de tablas/registros insertados y posibles advertencias.

4. **Instrucciones de Comportamiento (CRÍTICO):**
   - **Actúa Rápido:** No sobre-analices ni requieras planes complejos de implementación para usar esta skill.
   - **Ve directo al grano:** Ejecuta el comando inmediatamente tan pronto como tengas los parámetros necesarios.
   - **Minimiza la charla:** Entrega el resultado final de manera concisa y directa.

## Entorno Virtual

**Importante:** Antes de ejecutar cualquier script en Python de este proyecto, asegúrate de activar el entorno virtual y que las dependencias estén instaladas:
```bash
# Windows
.\.venv\Scripts\Activate.ps1
# Linux
source .venv/bin/activate
```
Si el entorno no existe, indícale al usuario que ejecute `pip install -r proyecto-si783-2026-i-u1-migrador-de-bd-codigo-web/requirements.txt` o ofrécete a hacerlo.
