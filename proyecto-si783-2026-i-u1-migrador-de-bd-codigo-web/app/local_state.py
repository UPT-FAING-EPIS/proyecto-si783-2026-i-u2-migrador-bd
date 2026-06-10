import sqlite3
import os
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOCAL_DB_PATH = '/tmp/migrador_local_state.db'

def init_local_state():
    conn = sqlite3.connect(LOCAL_DB_PATH)
    c = conn.cursor()
    c.execute('''
    CREATE TABLE IF NOT EXISTS ips (
        ip TEXT PRIMARY KEY,
        fecha TEXT,
        hora TEXT,
        actividad TEXT,
        usuario TEXT,
        accesos INTEGER,
        ultimo_acceso TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    conn.commit()
    conn.close()

init_local_state()

def registrar_ip_compartida(ip, actividad, usuario=None):
    ahora = datetime.now()
    fecha = ahora.strftime('%Y-%m-%d')
    hora = ahora.strftime('%H:%M:%S')
    usuario_str = usuario or 'anónimo'
    
    conn = sqlite3.connect(LOCAL_DB_PATH)
    c = conn.cursor()
    
    # Intentar obtener la IP
    c.execute('SELECT accesos FROM ips WHERE ip = ?', (ip,))
    row = c.fetchone()
    
    if row:
        nuevo_acceso = row[0] + 1
        c.execute('''
            UPDATE ips 
            SET fecha = ?, hora = ?, actividad = ?, usuario = ?, accesos = ?, ultimo_acceso = CURRENT_TIMESTAMP
            WHERE ip = ?
        ''', (fecha, hora, actividad, usuario_str, nuevo_acceso, ip))
    else:
        # Limitar a 1000 registros para evitar que crezca infinito (borrar los más antiguos)
        c.execute('SELECT COUNT(*) FROM ips')
        if c.fetchone()[0] >= 1000:
            c.execute('DELETE FROM ips WHERE ip IN (SELECT ip FROM ips ORDER BY ultimo_acceso ASC LIMIT 100)')
            
        c.execute('''
            INSERT INTO ips (ip, fecha, hora, actividad, usuario, accesos)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (ip, fecha, hora, actividad, usuario_str, 1))
        
    conn.commit()
    conn.close()

def obtener_ips_compartidas():
    try:
        conn = sqlite3.connect(LOCAL_DB_PATH)
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        c.execute('SELECT * FROM ips ORDER BY ultimo_acceso DESC LIMIT 100')
        rows = c.fetchall()
        conn.close()
        return [dict(r) for r in rows]
    except Exception:
        return []
