import os
import json
import uuid
import threading
from datetime import datetime
from flask import Blueprint, request, jsonify, send_file, current_app
from werkzeug.utils import secure_filename

from utilidades.detector import DetectorBaseDatos
from extraccion.conector import ConectorOrigen
from transformacion.mapeador import MapeadorDatos
from carga.cargador import CargadorDestino

api_v1 = Blueprint('api_v1', __name__, url_prefix='/api/v1')

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
API_UPLOADS_DIR = os.path.join(BASE_DIR, 'uploads', 'api_jobs')
os.makedirs(API_UPLOADS_DIR, exist_ok=True)

def _get_job_file(job_id: str) -> str:
    return os.path.join(API_UPLOADS_DIR, f"{job_id}.json")

def _update_job_status(job_id: str, data: dict):
    filepath = _get_job_file(job_id)
    state = {}
    if os.path.exists(filepath):
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                state = json.load(f)
        except Exception:
            pass
    state.update(data)
    state['updated_at'] = datetime.now().isoformat()
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(state, f, ensure_ascii=False, indent=2)

def _get_job_status(job_id: str) -> dict:
    filepath = _get_job_file(job_id)
    if os.path.exists(filepath):
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            return None
    return None

def ejecutar_migracion_background(job_id: str, ruta_archivo: str, nombre_archivo: str, motor_destino: str):
    try:
        _update_job_status(job_id, {"status": "processing", "progress": 5})
        
        tipo, mensaje, _ = DetectorBaseDatos.detectar(ruta_archivo, nombre_archivo)
        if tipo == 'Desconocido' or tipo == 'SQL Server Backup':
            _update_job_status(job_id, {"status": "error", "mensaje": f"Archivo no soportado: {mensaje}"})
            return

        origen = ConectorOrigen(ruta_archivo, tipo)
        if not origen.tablas:
            _update_job_status(job_id, {"status": "error", "mensaje": "El archivo origen no contiene tablas válidas."})
            return

        destino = CargadorDestino(motor=motor_destino)
        if origen.esquema:
            destino.crear_estructura(origen.esquema)
            
        _update_job_status(job_id, {"status": "processing", "progress": 10})
        
        total_tablas = len(origen.tablas)
        metricas = {"tablas_ok": 0, "extraidos": 0, "cargados": 0, "errores": 0}
        
        for idx, tabla in enumerate(origen.tablas):
            progreso = int(((idx + 1) / total_tablas) * 80) + 10  # 10% a 90%
            _update_job_status(job_id, {"progress": progreso, "current_table": tabla})
            
            try:
                for chunk_df in origen.extraer_datos_chunked(tabla, chunksize=10000):
                    if not chunk_df.empty:
                        filas = len(chunk_df)
                        metricas["extraidos"] += filas
                        chunk_df = MapeadorDatos.limpiar_dataframe(chunk_df)
                        cargados = destino.cargar_tabla(tabla, chunk_df)
                        metricas["cargados"] += cargados
                metricas["tablas_ok"] += 1
            except Exception as e:
                metricas["errores"] += 1
                
            _update_job_status(job_id, {"metricas": metricas})
            
        _update_job_status(job_id, {"status": "processing", "progress": 95, "mensaje": "Generando script final..."})
        
        # Objetos
        if hasattr(origen, 'vistas'): destino.crear_vistas(origen.vistas)
        if hasattr(origen, 'triggers'): destino.crear_triggers(origen.triggers)
        if hasattr(origen, 'procedimientos'): destino.crear_procedimientos(origen.procedimientos)
        if hasattr(origen, 'funciones'): destino.crear_funciones(origen.funciones)
        if hasattr(origen, 'indices'): destino.crear_indices(origen.indices)
        
        archivo_generado, ext, mime_type, is_file = destino.generar_export()
        
        output_file_path = archivo_generado
        if not is_file and archivo_generado:
            # Si generó texto, guardarlo a disco
            ruta_temp = os.path.join(API_UPLOADS_DIR, f"output_{job_id}{ext}")
            with open(ruta_temp, 'w', encoding='utf-8') as f:
                f.write(archivo_generado)
            output_file_path = ruta_temp
        
        _update_job_status(job_id, {
            "status": "completed", 
            "progress": 100, 
            "output_file": output_file_path,
            "output_ext": ext,
            "output_mime": mime_type
        })
        
    except Exception as e:
        _update_job_status(job_id, {"status": "error", "mensaje": str(e)})


@api_v1.route('/migrations/start', methods=['POST'])
def start_migration():
    if 'file' not in request.files:
        return jsonify({"estado": "error", "mensaje": "Falta el campo 'file'"}), 400
    
    motor_destino = request.form.get('motor_destino')
    if not motor_destino:
        return jsonify({"estado": "error", "mensaje": "Falta el campo 'motor_destino'"}), 400
        
    archivo = request.files['file']
    if archivo.filename == '':
        return jsonify({"estado": "error", "mensaje": "Archivo vacío"}), 400
        
    job_id = str(uuid.uuid4())
    nombre_archivo = secure_filename(archivo.filename)
    ruta_archivo = os.path.join(API_UPLOADS_DIR, f"{job_id}_{nombre_archivo}")
    
    try:
        archivo.save(ruta_archivo)
    except Exception as e:
        return jsonify({"estado": "error", "mensaje": f"Error al guardar archivo: {str(e)}"}), 500
        
    _update_job_status(job_id, {
        "job_id": job_id,
        "status": "pending",
        "progress": 0,
        "motor_destino": motor_destino,
        "archivo_origen": nombre_archivo
    })
    
    # Iniciar background
    thread = threading.Thread(target=ejecutar_migracion_background, args=(job_id, ruta_archivo, nombre_archivo, motor_destino))
    thread.daemon = True
    thread.start()
    
    return jsonify({
        "estado": "exito",
        "job_id": job_id,
        "mensaje": "Migración iniciada en segundo plano"
    }), 202

@api_v1.route('/migrations/<job_id>/status', methods=['GET'])
def get_migration_status(job_id):
    status = _get_job_status(job_id)
    if not status:
        return jsonify({"estado": "error", "mensaje": "Job no encontrado"}), 404
        
    return jsonify(status)

@api_v1.route('/migrations/<job_id>/download', methods=['GET'])
def download_migration(job_id):
    status = _get_job_status(job_id)
    if not status:
        return jsonify({"estado": "error", "mensaje": "Job no encontrado"}), 404
        
    if status.get("status") != "completed":
        return jsonify({"estado": "error", "mensaje": "La migración no ha finalizado o tiene errores"}), 400
        
    output_file = status.get("output_file")
    output_ext = status.get("output_ext", ".sql")
    mime_type = status.get("output_mime", "application/octet-stream")
    
    # Si la ruta existe (caso SQLite intermedio o texto guardado en disco)
    if output_file and os.path.exists(output_file):
        return send_file(
            output_file, 
            as_attachment=True, 
            download_name=f"migracion_{job_id}{output_ext}",
            mimetype=mime_type
        )
        
    return jsonify({"estado": "error", "mensaje": "No se pudo generar el archivo de salida"}), 500
