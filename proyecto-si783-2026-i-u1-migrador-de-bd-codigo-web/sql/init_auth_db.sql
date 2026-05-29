-- Script SQL para crear la base de datos de autenticación usada por la aplicación
-- Ruta esperada por la app: ../auth.db (junto a la carpeta `proyecto-si783-2026-i-u1-migrador-de-bd-codigo-web`/app)

PRAGMA foreign_keys = ON;

-- Tabla usuarios
CREATE TABLE IF NOT EXISTS usuarios (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    usuario TEXT UNIQUE NOT NULL,
    email TEXT UNIQUE NOT NULL,
    contraseña TEXT,
    rol TEXT NOT NULL DEFAULT 'usuario',
    creado_en TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    activo BOOLEAN DEFAULT 1,
    verification_code TEXT,
    verified BOOLEAN DEFAULT 0
);

-- Tabla de cuentas OAuth vinculadas
CREATE TABLE IF NOT EXISTS oauth_usuarios (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    usuario_id INTEGER NOT NULL,
    proveedor TEXT NOT NULL,
    proveedor_id TEXT NOT NULL,
    email TEXT NOT NULL,
    nombre TEXT,
    foto_url TEXT,
    creado_en TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (usuario_id) REFERENCES usuarios(id),
    UNIQUE(proveedor, proveedor_id)
);

-- Insertar administrador por defecto
-- Contraseña por defecto: admin123 (hash generado con Werkzeug scrypt)
INSERT INTO usuarios (usuario, email, contraseña, rol, verified)
VALUES (
    'admin',
    'admin@migrador.local',
    'scrypt:32768:8:1$wLvzGVwjt3SeXwXU$669cb1024a0c395efe49515a9fec819f6d0bc7ead76eeeb3f9ead8ab38d171d9fde6008f5c7d6c51669132d376ed0e269f05541c45ac7a5098a6ca8bbdddc294',
    'admin',
    1
);

-- Fin del script
