import os
import sys

try:
    os.chdir('/opt/migrador-bd')
except:
    pass

sys.path.insert(0, '.')

from dotenv import load_dotenv
load_dotenv('.env')

from app import crear_app
from app.auth import get_mysql_conn

def fix_mysql():
    print("Forzando actualizacion de MySQL...")
    app = crear_app()
    with app.app_context():
        try:
            conn = get_mysql_conn()
            cursor = conn.cursor()
            
            queries = [
                "ALTER TABLE usuarios ADD COLUMN foto_perfil LONGTEXT",
                "ALTER TABLE usuarios ADD COLUMN descripcion VARCHAR(500)",
                "ALTER TABLE usuarios ADD COLUMN github_url VARCHAR(255)"
            ]
            
            for q in queries:
                try:
                    cursor.execute(q)
                    conn.commit()
                    print(f"[EXITO] {q}")
                except Exception as e:
                    print(f"[IGNORADO - Tal vez ya existe] Error al ejecutar '{q}': {e}")
                    
            cursor.close()
            conn.close()
            print("========================================")
            print("Base de datos MySQL reparada con exito.")
            print("========================================")
        except Exception as e:
            print(f"[ERROR FATAL] No se pudo conectar a MySQL: {e}")

if __name__ == '__main__':
    fix_mysql()
