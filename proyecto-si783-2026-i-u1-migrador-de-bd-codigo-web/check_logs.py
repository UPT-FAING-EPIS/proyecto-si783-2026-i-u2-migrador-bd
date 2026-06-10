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

def run_logs():
    app = crear_app()
    with app.app_context():
        try:
            logs = run_query('SELECT fecha, nivel, mensaje FROM logs ORDER BY id DESC LIMIT 10', fetchall=True)
            print("=== ULTIMOS 10 LOGS ===")
            for log in logs:
                print(f"[{log[0]}] {log[1]}: {log[2]}")
        except Exception as e:
            print(f"Error reading logs: {e}")

if __name__ == '__main__':
    run_logs()
