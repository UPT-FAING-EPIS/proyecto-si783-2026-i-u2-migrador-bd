import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), 'auth.db')

def actualizar_bd():
    """Actualiza la base de datos para agregar columnas de verificación."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    try:
        # Verificar si las columnas ya existen
        c.execute("PRAGMA table_info(usuarios)")
        columns = [column[1] for column in c.fetchall()]

        # Agregar columna verification_code si no existe
        if 'verification_code' not in columns:
            print("Agregando columna verification_code...")
            c.execute("ALTER TABLE usuarios ADD COLUMN verification_code TEXT")

        # Agregar columna verified si no existe
        if 'verified' not in columns:
            print("Agregando columna verified...")
            c.execute("ALTER TABLE usuarios ADD COLUMN verified BOOLEAN DEFAULT 0")

        # Actualizar usuarios existentes para que estén verificados (solo admin por defecto)
        print("Actualizando usuarios existentes...")
        c.execute("UPDATE usuarios SET verified = 1 WHERE rol = 'admin'")

        conn.commit()
        print("Base de datos actualizada exitosamente!")

    except Exception as e:
        print(f"Error actualizando base de datos: {e}")
        conn.rollback()

    finally:
        conn.close()

if __name__ == "__main__":
    actualizar_bd()