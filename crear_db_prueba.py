import sqlite3

# Crear o conectar a una base de datos de prueba
conn = sqlite3.connect('test.sqlite')
cursor = conn.cursor()

# Crear una tabla de prueba
cursor.execute('''
CREATE TABLE IF NOT EXISTS usuarios (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre TEXT NOT NULL,
    email TEXT NOT NULL
)
''')

# Insertar un par de registros de prueba
cursor.execute("INSERT INTO usuarios (nombre, email) VALUES ('Juan Perez', 'juan@ejemplo.com')")
cursor.execute("INSERT INTO usuarios (nombre, email) VALUES ('Maria Lopez', 'maria@ejemplo.com')")

conn.commit()
conn.close()
print("Base de datos test.sqlite creada con éxito.")
