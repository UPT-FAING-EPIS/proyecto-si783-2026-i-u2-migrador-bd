import os
import sys

# Asegurarse de que estamos en el directorio correcto
try:
    os.chdir('/opt/migrador-bd')
except:
    pass

sys.path.insert(0, '.')

from app import crear_app
from app.auth import get_mysql_conn, USE_MYSQL, DB_PATH
import sqlite3

def run_fix():
    print("Iniciando diagnostico de la base de datos...")
    print(f"Usando MySQL: {USE_MYSQL}")
    
    app = crear_app()
    with app.app_context():
        if USE_MYSQL:
            try:
                conn = get_mysql_conn()
                cursor = conn.cursor()
                print("Conexion a MySQL exitosa.")
                
                queries = [
                    "ALTER TABLE usuarios ADD COLUMN foto_perfil LONGTEXT",
                    "ALTER TABLE usuarios ADD COLUMN descripcion VARCHAR(500)",
                    "ALTER TABLE usuarios ADD COLUMN github_url VARCHAR(255)"
                ]
                
                for q in queries:
                    try:
                        cursor.execute(q)
                        conn.commit()
                        print(f"[OK] Se agrego columna: {q}")
                    except Exception as e:
                        print(f"[INFO] No se pudo agregar (tal vez ya existe): {str(e)}")
                        
                cursor.close()
                conn.close()
                print("Proceso de MySQL terminado.")
            except Exception as e:
                print(f"[ERROR CRITICO] No se pudo conectar a MySQL: {str(e)}")
        else:
            print(f"Usando SQLite. Ruta: {DB_PATH}")
            try:
                conn = sqlite3.connect(DB_PATH)
                c = conn.cursor()
                
                queries = [
                    "ALTER TABLE usuarios ADD COLUMN foto_perfil TEXT",
                    "ALTER TABLE usuarios ADD COLUMN descripcion TEXT",
                    "ALTER TABLE usuarios ADD COLUMN github_url TEXT"
                ]
                
                for q in queries:
                    try:
                        c.execute(q)
                        conn.commit()
                        print(f"[OK] Se agrego columna: {q}")
                    except Exception as e:
                        print(f"[INFO] No se pudo agregar (tal vez ya existe): {str(e)}")
                        
                conn.close()
                print("Proceso de SQLite terminado.")
            except Exception as e:
                print(f"[ERROR CRITICO] No se pudo conectar o modificar SQLite: {str(e)}")

if __name__ == '__main__':
    run_fix()
