#!/usr/bin/env python
"""Test de nuevos motores de BD"""

import sys
sys.path.insert(0, '.')

from carga.cargador import CargadorDestino

# Prueba de exportación para los nuevos motores
motores_nuevos = ['Snowflake', 'Amazon Redshift', 'Azure SQL Database', 'IBM Db2', 'Google BigQuery', 'MongoDB Atlas']

print("=== Inicialización de exportadores ===")
for motor in motores_nuevos:
    try:
        exportador = CargadorDestino(motor)
        print(f'✓ {motor}: Exportador inicializado')
    except Exception as e:
        print(f'✗ {motor}: Error - {e}')

# Prueba de métodos de adaptación SQL
print("\n=== Prueba de métodos de adaptación SQL ===")
exportador = CargadorDestino('snowflake')
sql_test = 'CREATE TABLE IF NOT EXISTS test (id INTEGER PRIMARY KEY, nombre VARCHAR(100))'

for motor in motores_nuevos[:5]:  # Solo SQL engines
    try:
        sql_adaptado = exportador._adaptar_sql_objeto(sql_test, motor)
        print(f'✓ {motor}: SQL adaptado correctamente')
    except Exception as e:
        print(f'✗ {motor}: Error - {e}')

print("\n=== Mapeo de tipos de datos ===")
motores_test = {
    'Snowflake': ['INTEGER', 'VARCHAR', 'BLOB', 'FLOAT'],
    'Amazon Redshift': ['INTEGER', 'VARCHAR', 'BLOB', 'FLOAT'],
    'Azure SQL Database': ['INTEGER', 'VARCHAR', 'BLOB', 'FLOAT'],
    'IBM Db2': ['INTEGER', 'VARCHAR', 'BLOB', 'FLOAT'],
    'Google BigQuery': ['INTEGER', 'VARCHAR', 'BLOB', 'FLOAT'],
}

for motor, tipos in motores_test.items():
    try:
        resultados = []
        for tipo_origen in tipos:
            tipo_dest = exportador._tipo_sql_destino(tipo_origen, motor.lower())
            resultados.append(f'{tipo_origen}→{tipo_dest}')
        print(f'{motor}: {", ".join(resultados)}')
    except Exception as e:
        print(f'✗ {motor}: Error - {e}')

print("\n=== Prueba de quoted identifiers ===")
test_ident = "tabla_prueba"
for motor in motores_nuevos[:5]:  # Solo SQL engines
    try:
        quoted = exportador._quote_ident(test_ident, motor.lower())
        print(f'{motor}: {quoted}')
    except Exception as e:
        print(f'✗ {motor}: Error - {e}')

print("\n✓ Todas las pruebas completadas")
