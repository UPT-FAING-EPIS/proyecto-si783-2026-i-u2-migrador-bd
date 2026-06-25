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
    'sqlite':     'SQLite',
    'mysql':      'MySQL',
    'postgres':   'PostgreSQL',
    'postgresql': 'PostgreSQL',
    'sql':        'SQL Generico',
    'mssql':      'Microsoft SQL Server',
    'oracle':     'Oracle',
    'csv':        'CSV',
    'excel':      'Excel',
    'mongodb':    'MongoDB',
}

def main():
    parser = argparse.ArgumentParser(description="CLI Migrador BD para la Skill IA")
    parser.add_argument("--source",      required=True, help="Ruta o conexión de origen")
    parser.add_argument("--dest",        required=True, help="Ruta o conexión de destino (nombre del archivo de salida)")
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
        tablas  = origen.tablas    # Las tablas se auto-descubren en __init__
        esquema = origen.esquema
        print(f"✅ Tablas encontradas ({len(tablas)}): {tablas}")

        if not tablas:
            print("⚠️  No se encontraron tablas. Verifica el archivo/conexión de origen.")
            sys.exit(0)

        # 2. Carga en destino (CargadorDestino solo recibe el tipo de motor)
        print(f"Conectando al destino ({tipo_dest})...")
        destino = CargadorDestino(motor_destino=tipo_dest)
        destino.tabla_a_esquema = origen.tabla_a_esquema

        # Pasar objetos extra si existen (vistas, triggers, etc.)
        if origen.vistas:
            destino._stored_objs["vistas"] = origen.vistas
        if origen.triggers:
            destino._stored_objs["triggers"] = origen.triggers
        if origen.procedimientos:
            destino._stored_objs["procedimientos"] = origen.procedimientos
        if origen.funciones:
            destino._stored_objs["funciones"] = origen.funciones
        if origen.indices:
            destino._stored_objs["indices"] = origen.indices

        # 3. Crear la estructura (tablas vacías) en el destino
        print("Creando estructura en el destino...")
        destino.crear_estructura(esquema)

        # 4. Migrar datos tabla por tabla usando chunks
        print("Cargando datos tabla por tabla...")
        total_filas = 0
        for tabla in tablas:
            filas_tabla = 0
            for chunk in origen.extraer_datos_chunked(tabla):
                if not chunk.empty:
                    chunk_limpio = MapeadorDatos.limpiar_dataframe(chunk)
                    destino.cargar_tabla(tabla, chunk_limpio, esquema)
                    filas_tabla += len(chunk_limpio)
                    total_filas += len(chunk_limpio)
            print(f"  → {tabla}: {filas_tabla} fila(s) migradas")

        # 5. Exportar resultado final
        ruta_salida = destino.get_ruta_salida() if hasattr(destino, 'get_ruta_salida') else destino.ruta_salida
        print(f"\n✅ Migración completada exitosamente.")
        print(f"   Total filas migradas: {total_filas}")
        print(f"   Archivo de salida generado en: {ruta_salida}")

    except Exception as e:
        print(f"Error durante la migración: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
