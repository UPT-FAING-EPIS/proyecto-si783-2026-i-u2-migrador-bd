# Arquitectura API REST v1 para Migrador-BD

Este documento detalla la estructura para exponer la funcionalidad de Migrador-BD mediante endpoints RESTful asíncronos.

## Arquitectura y Flujo

Dado que el servidor utiliza múltiples workers (Gunicorn), la API debe ser completamente **stateless** (sin estado). En lugar de usar la memoria, las tareas se gestionan mediante un sistema basado en Jobs.

1. **El Cliente** sube un archivo y el motor destino a `/api/v1/migrations/start`.
2. **El Servidor** guarda el archivo y crea un registro del Job en disco o base de datos (ej. `uploads/jobs/123e4567.json`), luego lanza un hilo de ejecución en segundo plano y responde inmediatamente con el `job_id`.
3. **El Cliente** hace polling periódicamente a `/api/v1/migrations/{job_id}/status`. El endpoint simplemente lee el archivo del Job y devuelve el estado (`pending`, `processing`, `completed`, `error`) y el progreso %.
4. **El Cliente**, al ver que el status es `completed`, solicita el archivo resultante en `/api/v1/migrations/{job_id}/download`.

---

## Especificación de Endpoints

### 1. Iniciar Migración
- **Ruta:** `POST /api/v1/migrations/start`
- **Content-Type:** `multipart/form-data`
- **Parámetros requeridos:**
  - `file`: (Archivo) El archivo origen (.sql, .bak, etc.).
  - `motor_destino`: (String) El nombre del motor destino (ej. "PostgreSQL", "MongoDB").
- **Respuesta Exitosa (202 Accepted):**
  ```json
  {
      "estado": "exito",
      "job_id": "123e4567-e89b-12d3-a456-426614174000",
      "mensaje": "Migración iniciada en segundo plano"
  }
  ```

### 2. Consultar Estado
- **Ruta:** `GET /api/v1/migrations/{job_id}/status`
- **Content-Type:** `application/json`
- **Respuesta Exitosa (200 OK):**
  ```json
  {
      "job_id": "123e4567-e89b-12d3-a456-426614174000",
      "status": "processing",
      "progress": 45,
      "metricas": {
          "tablas_migradas": 5,
          "registros_migrados": 150000,
          "errores": 0
      }
  }
  ```

### 3. Descargar Script Resultante
- **Ruta:** `GET /api/v1/migrations/{job_id}/download`
- **Content-Type:** `application/json`
- **Respuesta:**
  - Si no ha terminado (400 Bad Request): `{"estado": "error", "mensaje": "Job aún en proceso"}`
  - Si terminó (200 OK): Descarga directa del archivo (attachment).

---

## Preguntas Abiertas para Implementación

Para escribir el código exacto, necesito que me confirmes estas dos preguntas de diseño:

1. **¿Deseas incluir Autenticación por ahora?** (Por ejemplo, requerir un `Authorization: Bearer <API_KEY>` en los headers) o lo hacemos abierto para pruebas.
2. **Modo de Operación:** La API, de momento, asumirá que la salida es siempre un "Script" para descargar. ¿Está bien o deseas incluir parámetros para inyectar los datos directamente enviando un Host/User/Pass?
