import requests
import time
import os
import sys

BASE_URL = 'http://localhost:5000/api/v1/migrations'

def test_api():
    print("=== TESTING MIGRATION API V1 ===")
    
    # 1. Crear un archivo SQL de prueba
    test_file_path = "test_source.sql"
    with open(test_file_path, "w") as f:
        f.write("CREATE TABLE usuarios (id INT, nombre VARCHAR(100));\n")
        f.write("INSERT INTO usuarios VALUES (1, 'Alice'), (2, 'Bob');\n")
        
    print(f"[*] Archivo de prueba creado: {test_file_path}")
    
    # 2. Iniciar la migración
    print("[*] Iniciando migración a MongoDB...")
    try:
        with open(test_file_path, "rb") as f:
            files = {'file': (test_file_path, f, 'application/sql')}
            data = {'motor_destino': 'MongoDB'}
            resp = requests.post(f"{BASE_URL}/start", files=files, data=data)
            
        if resp.status_code != 202:
            print(f"[!] Error iniciando migración: {resp.status_code} - {resp.text}")
            sys.exit(1)
            
        resp_data = resp.json()
        job_id = resp_data.get('job_id')
        print(f"[+] Migración iniciada exitosamente! Job ID: {job_id}")
        
    except requests.exceptions.ConnectionError:
        print("[!] Error: Servidor Flask no está corriendo en localhost:5000")
        sys.exit(1)
        
    # 3. Hacer polling del status
    print("[*] Consultando progreso...")
    max_retries = 20
    status_data = {}
    
    for _ in range(max_retries):
        resp = requests.get(f"{BASE_URL}/{job_id}/status")
        status_data = resp.json()
        status = status_data.get('status')
        progress = status_data.get('progress', 0)
        
        print(f"    -> Estado: {status} | Progreso: {progress}%")
        
        if status in ['completed', 'error']:
            break
            
        time.sleep(1)
        
    if status_data.get('status') != 'completed':
        print(f"[!] La migración no completó con éxito. Estado final: {status_data}")
        sys.exit(1)
        
    print("[+] Migración completada!")
    
    # 4. Descargar el script
    print("[*] Descargando archivo resultante...")
    resp = requests.get(f"{BASE_URL}/{job_id}/download")
    if resp.status_code == 200:
        out_filename = f"resultado_{job_id}.json"
        with open(out_filename, 'wb') as f:
            f.write(resp.content)
        print(f"[+] Archivo descargado exitosamente: {out_filename}")
        print(f"[+] Tamaño: {os.path.getsize(out_filename)} bytes")
    else:
        print(f"[!] Error descargando archivo: {resp.status_code} - {resp.text}")

    # Limpiar archivos de prueba
    if os.path.exists(test_file_path):
        os.remove(test_file_path)
    if os.path.exists(out_filename):
        os.remove(out_filename)

if __name__ == '__main__':
    test_api()
