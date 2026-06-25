import argparse
import sys
import os
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

# Mapeo de nombre corto al nombre exacto que espera el proyecto
TIPO_MAP = {
    'sqlite':    'SQLite',
    'mysql':     'MySQL',
    'postgres':  'PostgreSQL',
    'postgresql':'PostgreSQL',
    'sql':       'SQL Generico',
    'mssql':     'Microsoft SQL Server',
    'oracle':    'Oracle',
    'csv':       'CSV',
    'excel':     'Excel',
    'mongodb':   'MongoDB',
}

def main():
    parser = argparse.ArgumentParser(description="CLI Migrador BD para la Skill IA")
    parser.add_argument("--source",      required=True, help="Ruta o conexión de origen")
    parser.add_argument("--dest",        required=True, help="Ruta o conexión de destino")
    parser.add_argument("--tipo-origen", required=True, help="Tipo de BD origen (sqlite, mysql, postgres...)")
    parser.add_argument("--tipo-dest",   required=True, help="Tipo de BD destino (sqlite, mysql, postgres...)")
    args = parser.parse_args()

    tipo_origen = TIPO_MAP.get(args.tipo_origen.lower(), args.tipo_origen)
    tipo_dest   = TIPO_MAP.get(args.tipo_dest.lower(),   args.tipo_dest)

    print(f"Iniciando migración desde {tipo_origen} ({args.source}) → {tipo_dest} ({args.dest})...")

    try:
        # 1. Extracción: crear el conector y descubrir tablas
        print("Conectando al origen y descubriendo tablas...")
        origen = ConectorOrigen(ruta=args.source, tipo=tipo_origen)
        tablas = origen.tablas          # Las tablas se descubren en __init__
        esquema = origen.esquema
        print(f"✅ Tablas encontradas ({len(tablas)}): {tablas}")

        if not tablas:
            print("⚠️  No se encontraron tablas en el origen. Verifica el archivo/conexión.")
            sys.exit(0)

        # 2. Mapeo de tipos
        print("Mapeando tipos de datos...")
        mapeador = MapeadorDatos(esquema=esquema, tipo_origen=tipo_origen, tipo_destino=tipo_dest)
        esquema_mapeado = mapeador.mapear()

        # 3. Carga en destino
        print("Creando estructura en destino...")
        destino = CargadorDestino(ruta=args.dest, tipo=tipo_dest)
        destino.crear_estructura(esquema_mapeado)

        print("Cargando datos tabla por tabla...")
        total_filas = 0
        for tabla in tablas:
            for chunk in origen.extraer_datos_chunked(tabla):
                if not chunk.empty:
                    destino.cargar_tabla(tabla, chunk, esquema_mapeado)
                    total_filas += len(chunk)
                    print(f"  → {tabla}: {len(chunk)} fila(s) migradas")

        print(f"\n✅ Migración completada. Total filas migradas: {total_filas}")

    except Exception as e:
        print(f"Error durante la migración: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
