import argparse
import sys
import os
import shutil
from pathlib import Path

# Forzar UTF-8 en stdout/stderr para que los emojis funcionen en Windows y Linux
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8')


# Añadimos la ruta del proyecto web para poder importar sus módulos
proyecto_dir = Path(os.path.abspath(__file__)).parent.parent.parent.parent.parent / 'proyecto-si783-2026-i-u1-migrador-de-bd-codigo-web'
sys.path.insert(0, str(proyecto_dir))

try:
    from extraccion.conector import ConectorOrigen
    from carga.cargador import CargadorDestino
    from transformacion.mapeador import MapeadorDatos
except ImportError as e:
    print(f"Error importando módulos del proyecto: {e}")
    sys.exit(1)

# Mapeo extensión → tipo de BD origen (auto-detección)
EXT_ORIGEN_MAP = {
    '.sqlite': 'SQLite',
    '.db':     'SQLite',
    '.sql':    'SQL Generico',
    '.csv':    'CSV',
    '.xlsx':   'Excel',
    '.xls':    'Excel',
    '.json':   'MongoDB',
    '.bson':   'MongoDB',
}

def detectar_tipo_origen(ruta: str) -> str:
    """Detecta automáticamente el tipo de BD por la extensión del archivo."""
    ext = Path(ruta).suffix.lower()
    tipo = EXT_ORIGEN_MAP.get(ext)
    if tipo:
        return tipo
    # Si no tiene extensión conocida, intenta por nombre de host (conexión remota)
    ruta_l = ruta.lower()
    if 'mysql' in ruta_l or '3306' in ruta_l:       return 'MySQL'
    if 'postgres' in ruta_l or '5432' in ruta_l:    return 'PostgreSQL'
    if 'mongo' in ruta_l or '27017' in ruta_l:      return 'MongoDB'
    if 'redis' in ruta_l or '6379' in ruta_l:       return 'Redis'
    if 'elastic' in ruta_l or '9200' in ruta_l:     return 'Elasticsearch'
    return 'SQLite'  # fallback seguro


# Mapeo de nombre corto → string que usa generar_export() internamente
# generar_export() comprueba subcadenas en motor.lower()
EXPORT_MOTOR_MAP = {
    'SQLite':                 'sqlite',
    'MySQL':                  'mysql',
    'PostgreSQL':             'postgres',
    'SQL Generico':           'mysql',       # Produce SQL ANSI usando rama mysql
    'Microsoft SQL Server':   'sql server',
    'Oracle':                 'oracle',
    'MongoDB':                'mongodb',
    'Elasticsearch':          'elasticsearch',
    'Cassandra':              'cassandra',
    'Redis':                  'redis',
    # por si el usuario escribe directamente
    'CSV':                    'sqlite',
    'Excel':                  'sqlite',
}

def main():
    parser = argparse.ArgumentParser(description="CLI Migrador BD - Skill IA")
    parser.add_argument("--source",      required=True, help="Ruta o conexión de origen")
    parser.add_argument("--dest",        required=True, help="Nombre base del archivo de salida (sin extensión)")
    parser.add_argument("--tipo-dest",   required=True, help="Tipo BD destino: sqlite, mysql, postgres, mongodb, redis, cassandra, elasticsearch")
    args = parser.parse_args()

    # Auto-detectar tipo de origen por extensión
    tipo_origen  = detectar_tipo_origen(args.source)

    DEST_MAP = {
        'sqlite': 'SQLite', 'mysql': 'MySQL', 'postgres': 'PostgreSQL',
        'postgresql': 'PostgreSQL', 'sql': 'SQL Generico',
        'sqlserver': 'Microsoft SQL Server', 'mssql': 'Microsoft SQL Server',
        'oracle': 'Oracle', 'mongodb': 'MongoDB', 'mongo': 'MongoDB',
        'elasticsearch': 'Elasticsearch', 'elastic': 'Elasticsearch',
        'cassandra': 'Cassandra', 'redis': 'Redis',
    }
    tipo_dest    = DEST_MAP.get(args.tipo_dest.lower().replace(' ', ''), args.tipo_dest)
    motor_export = EXPORT_MOTOR_MAP.get(tipo_dest, tipo_dest.lower())


    print(f"\n{'='*60}")
    print(f"  MIGRADOR BD")
    print(f"  Origen : {tipo_origen}  <--  {args.source}")
    print(f"  Destino: {tipo_dest}  -->  (motor export: {motor_export})")
    print(f"{'='*60}\n")


    # Carpeta de salida limpia (solo el archivo final, sin internos)
    output_dir = "output"
    os.makedirs(output_dir, exist_ok=True)

    try:
        # ── PASO 1: Extracción ───────────────────────────────────
        print("[1/4] Conectando al origen y descubriendo estructura...")
        origen = ConectorOrigen(ruta=args.source, tipo=tipo_origen)
        tablas  = origen.tablas
        esquema = origen.esquema
        print(f"      ✅ Tablas ({len(tablas)}): {tablas}")
        if origen.vistas:        print(f"      ✅ Vistas: {len(origen.vistas)}")
        if origen.triggers:      print(f"      ✅ Triggers: {len(origen.triggers)}")
        if origen.procedimientos:print(f"      ✅ Procedimientos: {len(origen.procedimientos)}")
        if origen.funciones:     print(f"      ✅ Funciones: {len(origen.funciones)}")
        if origen.indices:       print(f"      ✅ Índices: {len(origen.indices)}")

        if not tablas:
            print("      ⚠️  No se encontraron tablas. Verifica el archivo/conexión de origen.")
            sys.exit(0)

        # ── PASO 2: Crear estructura en destino ──────────────────
        print(f"\n[2/4] Preparando destino ({tipo_dest})...")
        destino = CargadorDestino(motor_destino=tipo_dest)
        destino.tabla_a_esquema = origen.tabla_a_esquema
        destino.crear_estructura(esquema, origen.tabla_a_esquema)

        # Registrar objetos especiales
        if origen.vistas:        destino.crear_vistas(origen.vistas)
        if origen.triggers:      destino.crear_triggers(origen.triggers)
        if origen.procedimientos:destino.crear_procedimientos(origen.procedimientos)
        if origen.funciones:     destino.crear_funciones(origen.funciones)
        if origen.indices:       destino.crear_indices(origen.indices)
        print("      ✅ Estructura creada")

        # ── PASO 3: Migrar datos ─────────────────────────────────
        print(f"\n[3/4] Migrando datos ({len(tablas)} tabla(s))...")
        total_filas = 0
        errores = []
        for tabla in tablas:
            filas_tabla = 0
            try:
                for chunk in origen.extraer_datos_chunked(tabla):
                    if not chunk.empty:
                        chunk_limpio = MapeadorDatos.limpiar_dataframe(chunk)
                        destino.cargar_tabla(tabla, chunk_limpio)
                        filas_tabla += len(chunk_limpio)
                        total_filas += len(chunk_limpio)
                print(f"      → {tabla}: {filas_tabla} fila(s)")
            except Exception as e_tabla:
                errores.append(f"{tabla}: {e_tabla}")
                print(f"      ⚠️  Error en {tabla}: {e_tabla}")

        # ── PASO 4: Exportar al formato correcto del destino ─────
        print(f"\n[4/4] Exportando formato {motor_export.upper()}...")
        resultado, ext, mimetype, es_binario = destino.generar_export(motor_export)

        if not resultado:
            print("      ❌ Error: No se generó ningún archivo.")
            sys.exit(1)

        # Nombre limpio sin doble extensión
        nombre_base = Path(args.dest).stem   # quita extensión si ya tenía una
        nombre_salida = os.path.join(output_dir, f"{nombre_base}{ext}")

        if es_binario:
            # Archivo binario (SQLite .db) — copiar
            if os.path.exists(resultado):
                shutil.copy2(resultado, nombre_salida)
        else:
            # Texto (SQL, JSON, CQL, Redis) — escribir correctamente codificado
            with open(nombre_salida, 'w', encoding='utf-8') as f:
                f.write(resultado)

        print(f"\n{'='*60}")
        print(f"  ✅ MIGRACIÓN COMPLETADA")
        print(f"     Total filas migradas : {total_filas}")
        print(f"     Errores              : {len(errores)}")
        print(f"     Formato de salida    : {mimetype}")
        print(f"     📄 Archivo generado  : {nombre_salida}")
        print(f"{'='*60}\n")

        if errores:
            print("Detalle de errores:")
            for e in errores:
                print(f"  - {e}")

    except Exception as e:
        print(f"\n❌ Error fatal: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
