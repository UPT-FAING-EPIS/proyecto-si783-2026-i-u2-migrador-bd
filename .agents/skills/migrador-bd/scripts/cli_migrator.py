import argparse
import sys
import os
import shutil
from pathlib import Path

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

# Mapeo de nombre corto al nombre EXACTO que espera el proyecto
TIPO_MAP = {
    'sqlite':      'SQLite',
    'mysql':       'MySQL',
    'postgres':    'PostgreSQL',
    'postgresql':  'PostgreSQL',
    'sql':         'SQL Generico',
    'sqlgenerico': 'SQL Generico',
    'mssql':       'Microsoft SQL Server',
    'sqlserver':   'Microsoft SQL Server',
    'oracle':      'Oracle',
    'csv':         'CSV',
    'excel':       'Excel',
    'mongodb':     'MongoDB',
    'mongo':       'MongoDB',
    'elasticsearch': 'Elasticsearch',
    'elastic':     'Elasticsearch',
    'cassandra':   'Cassandra',
    'redis':       'Redis',
}

def main():
    parser = argparse.ArgumentParser(description="CLI Migrador BD - Skill IA")
    parser.add_argument("--source",      required=True, help="Ruta o conexión de origen")
    parser.add_argument("--dest",        required=True, help="Nombre del archivo de salida")
    parser.add_argument("--tipo-origen", required=True, help="Tipo de BD origen (sqlite, mysql, postgres, csv, excel, mongodb...)")
    parser.add_argument("--tipo-dest",   required=True, help="Tipo de BD destino (sqlite, mysql, postgres, mongodb, redis...)")
    args = parser.parse_args()

    tipo_origen = TIPO_MAP.get(args.tipo_origen.lower().replace(' ', ''), args.tipo_origen)
    tipo_dest   = TIPO_MAP.get(args.tipo_dest.lower().replace(' ', ''),   args.tipo_dest)

    print(f"\n{'='*55}")
    print(f"  MIGRADOR BD - Inicio de migración")
    print(f"  Origen : {tipo_origen}  →  {args.source}")
    print(f"  Destino: {tipo_dest}  →  {args.dest}")
    print(f"{'='*55}\n")

    try:
        # ── PASO 1: Extracción ──────────────────────────────────
        print("[1/4] Conectando al origen y descubriendo estructura...")
        origen = ConectorOrigen(ruta=args.source, tipo=tipo_origen)
        tablas  = origen.tablas
        esquema = origen.esquema
        print(f"      ✅ Tablas encontradas ({len(tablas)}): {tablas}")
        if origen.vistas:
            print(f"      ✅ Vistas encontradas: {len(origen.vistas)}")
        if origen.triggers:
            print(f"      ✅ Triggers encontrados: {len(origen.triggers)}")
        if origen.procedimientos:
            print(f"      ✅ Procedimientos encontrados: {len(origen.procedimientos)}")

        if not tablas:
            print("      ⚠️  No se encontraron tablas. Verifica el archivo/conexión de origen.")
            sys.exit(0)

        # ── PASO 2: Crear estructura en destino ─────────────────
        print(f"\n[2/4] Creando estructura en destino ({tipo_dest})...")
        destino = CargadorDestino(motor_destino=tipo_dest)
        destino.tabla_a_esquema = origen.tabla_a_esquema
        destino.crear_estructura(esquema, origen.tabla_a_esquema)

        # Registrar objetos especiales (vistas, triggers, procs, funciones, índices)
        if origen.vistas:        destino.crear_vistas(origen.vistas)
        if origen.triggers:      destino.crear_triggers(origen.triggers)
        if origen.procedimientos: destino.crear_procedimientos(origen.procedimientos)
        if origen.funciones:     destino.crear_funciones(origen.funciones)
        if origen.indices:       destino.crear_indices(origen.indices)
        print("      ✅ Estructura creada")

        # ── PASO 3: Cargar datos tabla por tabla ────────────────
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
                print(f"      ⚠️  Error en tabla {tabla}: {e_tabla}")

        # ── PASO 4: Exportar al formato final del destino ───────
        print(f"\n[4/4] Exportando al formato {tipo_dest}...")
        resultado, ext, mimetype, es_binario = destino.generar_export(tipo_dest)

        if not resultado:
            print("      ❌ Error: No se generó ningún archivo de exportación.")
            sys.exit(1)

        # Guardar en el directorio actual con el nombre que el usuario pidió
        nombre_salida = args.dest if args.dest.endswith(ext) else f"{args.dest}{ext}"
        if es_binario:
            # Es un archivo binario (ej: .db SQLite) — copiarlo al directorio actual
            if os.path.exists(resultado):
                shutil.copy2(resultado, nombre_salida)
        else:
            # Es texto (SQL, JSON, CQL, etc.) — escribirlo directamente
            with open(nombre_salida, 'w', encoding='utf-8') as f:
                f.write(resultado)

        print(f"\n{'='*55}")
        print(f"  ✅ Migración completada")
        print(f"     Total filas migradas : {total_filas}")
        print(f"     Errores              : {len(errores)}")
        print(f"     Archivo de salida    : {nombre_salida}  ({mimetype})")
        print(f"{'='*55}\n")

        if errores:
            print("Detalles de errores:")
            for e in errores:
                print(f"  - {e}")

    except Exception as e:
        print(f"\n❌ Error fatal durante la migración: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
