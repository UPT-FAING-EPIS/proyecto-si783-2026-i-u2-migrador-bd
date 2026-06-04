#!/usr/bin/env python3
"""Test de detección de tipos de base de datos para todos los motores soportados."""

import os
import sys
import tempfile
import json
from pathlib import Path
from utilidades.detector import DetectorBaseDatos

# Configurar encoding en la consola de Windows para evitar UnicodeEncodeError
if sys.stdout.encoding.lower() != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

def test_deteccion(nombre_archivo, contenido, tipo_esperado):
    """Crea un archivo temporal y lo prueba con el detector."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.sql', delete=False, encoding='utf-8') as f:
        f.write(contenido)
        temp_path = f.name
    
    try:
        tipo_detectado, mensaje, _ = DetectorBaseDatos.detectar(temp_path, nombre_archivo)
        estado = "✓" if tipo_esperado in tipo_detectado else "✗"
        print(f"{estado} {nombre_archivo:40} Esperado: {tipo_esperado:25} Detectado: {tipo_detectado}")
        return tipo_esperado in tipo_detectado
    finally:
        try:
            os.unlink(temp_path)
        except Exception as e:
            print(f"Warning: No se pudo eliminar archivo temporal {temp_path}: {e}")

print("=" * 110)
print("PRUEBAS DE DETECCIÓN DE TIPO DE BASE DE DATOS")
print("=" * 110)

# Pruebas para motores SQL relacionales
tests = [
    # HeidiSQL
    ("heidisql_dump.sql", """
    -- --------------------------------------------------------
    -- Host:                         127.0.0.1
    -- Versión del servidor:         10.4.24-MariaDB - mariadb.org binary distribution
    -- SO del servidor:              Win64
    -- HeidiSQL Versión:             11.3.0.6295
    -- --------------------------------------------------------
    CREATE TABLE IF NOT EXISTS `users` (
        `id` int(11) NOT NULL AUTO_INCREMENT,
        `name` varchar(50) DEFAULT NULL,
        PRIMARY KEY (`id`)
    );
    """, "MySQL"),

    # PostgreSQL
    ("postgresql.sql", """
    CREATE TABLE IF NOT EXISTS users (
        id SERIAL PRIMARY KEY,
        name VARCHAR(255) NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    INSERT INTO users (name) VALUES ('John');
    """, "PostgreSQL"),
    
    # MySQL
    ("mysql.sql", """
    CREATE TABLE IF NOT EXISTS users (
        id INT AUTO_INCREMENT PRIMARY KEY,
        name VARCHAR(255) NOT NULL ENGINE=INNODB,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    INSERT INTO users (name) VALUES ('John');
    """, "MySQL"),
    
    # SQL Server
    ("sqlserver.sql", """
    CREATE TABLE users (
        id INT PRIMARY KEY IDENTITY(1,1),
        name NVARCHAR(255) NOT NULL,
        created_at DATETIME DEFAULT GETDATE()
    );
    GO
    INSERT INTO users (name) VALUES ('John');
    GO
    """, "SQL Server"),
    
    # Oracle
    ("oracle.sql", """
    CREATE TABLE users (
        id NUMBER PRIMARY KEY,
        name VARCHAR2(255) NOT NULL,
        created_at DATE DEFAULT SYSDATE
    ) TABLESPACE users_ts;
    INSERT INTO users (id, name) VALUES (1, 'John');
    """, "Oracle"),
    
    # BigQuery
    ("bigquery.sql", """
    CREATE TABLE `project.dataset.users` (
        id INT64,
        name STRING,
        created_at TIMESTAMP
    );
    INSERT INTO `project.dataset.users` (id, name) VALUES (1, 'John');
    """, "BigQuery"),
    
    # Snowflake
    ("snowflake.sql", """
    CREATE TABLE users (
        id INT,
        name STRING,
        data VARIANT
    );
    INSERT INTO users (id, name) VALUES (1, 'John');
    """, "Snowflake"),
    
    # Amazon Redshift
    ("redshift.sql", """
    CREATE TABLE users (
        id INT,
        name VARCHAR(255),
        created_at TIMESTAMP
    )
    DISTKEY (id)
    SORTKEY (created_at);
    INSERT INTO users (id, name) VALUES (1, 'John');
    """, "Redshift"),
    
    # Cassandra
    ("cassandra.cql", """
    CREATE KEYSPACE IF NOT EXISTS myapp WITH replication = {'class':'SimpleStrategy', 'replication_factor' : 3};
    CREATE TABLE myapp.users (
        id UUID PRIMARY KEY,
        name TEXT,
        created_at TIMESTAMP
    );
    """, "Cassandra"),
    
    # SQL Genérico
    ("generic.sql", """
    CREATE TABLE users (
        id INTEGER PRIMARY KEY,
        name TEXT NOT NULL
    );
    INSERT INTO users (id, name) VALUES (1, 'John');
    """, "SQL Generico"),
]

# Ejecutar pruebas de SQL
print("\n[1] PRUEBAS DE DETECCIÓN SQL")
print("-" * 110)
sql_results = []
for nombre, contenido, esperado in tests:
    result = test_deteccion(nombre, contenido, esperado)
    sql_results.append(result)

# Pruebas para MongoDB/JSON
print("\n[2] PRUEBAS DE DETECCIÓN JSON/NDJSON")
print("-" * 110)

with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False, encoding='utf-8') as f:
    json.dump([
        {"_id": 1, "name": "John", "email": "john@example.com"},
        {"_id": 2, "name": "Jane", "email": "jane@example.com"}
    ], f)
    temp_path = f.name

tipo_detectado, mensaje, _ = DetectorBaseDatos.detectar(temp_path, "mongodb.json")
estado = "✓" if "MongoDB" in tipo_detectado else "✗"
print(f"{estado} mongodb.json                          Esperado: MongoDB              Detectado: {tipo_detectado}")
os.unlink(temp_path)

# NDJSON
with tempfile.NamedTemporaryFile(mode='w', suffix='.ndjson', delete=False, encoding='utf-8') as f:
    f.write('{"_id": 1, "name": "John"}\n')
    f.write('{"_id": 2, "name": "Jane"}\n')
    f.write('{"_id": 3, "name": "Bob"}\n')
    temp_path = f.name

tipo_detectado, mensaje, _ = DetectorBaseDatos.detectar(temp_path, "export.ndjson")
estado = "✓" if "MongoDB" in tipo_detectado else "✗"
print(f"{estado} export.ndjson                         Esperado: MongoDB              Detectado: {tipo_detectado}")
os.unlink(temp_path)

# Elasticsearch
with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False, encoding='utf-8') as f:
    json.dump({
        "hits": {
            "total": 2,
            "hits": [
                {"_index": "users", "_id": "1", "_source": {"name": "John"}},
                {"_index": "users", "_id": "2", "_source": {"name": "Jane"}}
            ]
        }
    }, f)
    temp_path = f.name

tipo_detectado, mensaje, _ = DetectorBaseDatos.detectar(temp_path, "elasticsearch.json")
estado = "✓" if "Elasticsearch" in tipo_detectado else "✗"
print(f"{estado} elasticsearch.json                    Esperado: Elasticsearch        Detectado: {tipo_detectado}")
os.unlink(temp_path)

print("\n" + "=" * 110)
print(f"RESUMEN: {sum(sql_results)}/{len(sql_results)} pruebas SQL exitosas")
print("=" * 110)
