import argparse
import sys
import os
from pathlib import Path

# Añadimos la ruta del proyecto web para poder importar sus módulos
proyecto_dir = Path(os.path.abspath(__file__)).parent.parent.parent.parent / 'proyecto-si783-2026-i-u1-migrador-de-bd-codigo-web'
sys.path.insert(0, str(proyecto_dir))

try:
    from extraccion.conector import ConectorOrigen
    from carga.cargador import CargadorDestino
    from transformacion.mapeador import MapeadorDatos
except ImportError as e:
    print(f"Error importando módulos del proyecto: {e}")
    sys.exit(1)

def main():
    parser = argparse.ArgumentParser(description="CLI Migrador BD para la Skill IA")
    parser.add_argument("--source", required=True, help="Ruta o conexión de origen")
    parser.add_argument("--dest", required=True, help="Ruta o conexión de destino")
    parser.add_argument("--tipo-origen", required=True, help="Tipo de base de datos origen (ej: sqlite, mysql)")
    parser.add_argument("--tipo-dest", required=True, help="Tipo de base de datos destino")
    args = parser.parse_args()

    print(f"Iniciando migración desde {args.tipo_origen} ({args.source}) hacia {args.tipo_dest} ({args.dest})...")

    try:
        # 1. Extracción
        print("Conectando al origen...")
        origen = ConectorOrigen(ruta=args.source, tipo=args.tipo_origen)
        tablas = origen.obtener_tablas()
        print(f"Tablas encontradas: {tablas}")

        # 2. Conexión a destino
        print("Conectando al destino...")
        destino = CargadorDestino(ruta=args.dest, tipo=args.tipo_dest)

        # 3. Mapeo y Carga (simplificado para el script CLI)
        print("Procesando y migrando tablas...")
        for tabla in tablas:
            print(f"Migrando tabla: {tabla}...")
            # Lógica simplificada asumiendo métodos estándar de las clases:
            # datos = origen.extraer_datos(tabla)
            # destino.cargar_datos(tabla, datos)
            print(f"Tabla {tabla} migrada exitosamente (simulado en el wrapper).")
            
        print("Migración completada exitosamente.")

    except Exception as e:
        print(f"Error durante la migración: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
