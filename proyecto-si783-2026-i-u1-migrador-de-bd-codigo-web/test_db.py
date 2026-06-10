import os
import sys

try:
    os.chdir('/opt/migrador-bd')
except:
    pass

sys.path.insert(0, '.')

from app import crear_app
from app.auth import get_mysql_conn, USE_MYSQL, DB_PATH, run_query
import sqlite3

def run_test():
    app = crear_app()
    with app.app_context():
        try:
            print("Probando UPDATE...")
            run_query('UPDATE usuarios SET descripcion = ? WHERE id = ?', ('Prueba desde test_db', 1), commit=True)
            print("[OK] UPDATE ejecutado correctamente")
        except Exception as e:
            print(f"[ERROR UPDATE] {type(e).__name__}: {str(e)}")
            
        try:
            print("Probando SELECT completo...")
            res = run_query('SELECT id, usuario, email, rol, foto_perfil, descripcion, github_url FROM usuarios WHERE id = ?', (1,), fetchone=True)
            print(f"[OK] SELECT completo: {res}")
            print(f"Longitud de res: {len(res) if res else 0}")
        except Exception as e:
            print(f"[ERROR SELECT] {type(e).__name__}: {str(e)}")

if __name__ == '__main__':
    run_test()
