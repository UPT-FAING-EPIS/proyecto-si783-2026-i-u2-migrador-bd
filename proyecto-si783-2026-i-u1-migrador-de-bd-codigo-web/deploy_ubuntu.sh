#!/bin/bash

# Script de despliegue para Ubuntu
# Uso: ./deploy_ubuntu.sh [puerto] [usuario] [directorio]
# Ejemplo: ./deploy_ubuntu.sh 8000 migrador /opt/migrador-bd

set -e

# Variables configurables
PUERTO=${1:-8000}
USUARIO=${2:-www-data}
DIRECTORIO=${3:-/opt/migrador-bd}
NOMBRE_SERVICIO="migrador-bd"

echo "=================================================="
echo "DESPLIEGUE DE MIGRADOR BD EN UBUNTU"
echo "=================================================="
echo "Puerto: $PUERTO"
echo "Usuario: $USUARIO"
echo "Directorio: $DIRECTORIO"
echo "Servicio: $NOMBRE_SERVICIO"
echo "=================================================="
echo ""

# 1. Actualizar sistema
echo "[1/7] Actualizando sistema..."
sudo apt-get update
sudo apt-get upgrade -y

# 2. Instalar dependencias
echo "[2/7] Instalando dependencias del sistema..."
sudo apt-get install -y \
    python3 \
    python3-pip \
    python3-venv \
    curl \
    wget \
    git \
    nginx \
    supervisor \
    sqlite3 \
    libpq-dev \
    mysql-client-core-8.0 \
    build-essential

# 3. Crear directorio y clonar/copiar proyecto
echo "[3/7] Preparando directorio del proyecto..."
sudo mkdir -p "$DIRECTORIO"
sudo chown "$USUARIO:$USUARIO" "$DIRECTORIO"

if [ ! -f "$DIRECTORIO/run.py" ]; then
    echo "Copiando archivos del proyecto..."
    cp -r ./* "$DIRECTORIO/" 2>/dev/null || true
fi

cd "$DIRECTORIO"

# 4. Crear y activar entorno virtual
echo "[4/7] Configurando entorno virtual Python..."
if [ ! -d "$DIRECTORIO/venv" ]; then
    python3 -m venv venv
fi

source venv/bin/activate

# 5. Instalar dependencias Python
echo "[5/7] Instalando dependencias Python..."
pip install --upgrade pip
pip install -r requirements.txt 2>/dev/null || pip install flask flask-socketio flask-cors python-dotenv werkzeug pandas sqlalchemy

# 6. Instalar Gunicorn
echo "[6/7] Instalando Gunicorn..."
pip install gunicorn

# 7. Crear archivo .env si no existe
echo "[7/7] Configurando variables de entorno..."
if [ ! -f "$DIRECTORIO/.env" ]; then
    cat > "$DIRECTORIO/.env" << EOF
FLASK_ENV=production
FLASK_APP=run.py
HOST=127.0.0.1
PORT=5000
SECRET_KEY=$(python3 -c 'import secrets; print(secrets.token_hex(32))')
EOF
    echo "✓ Archivo .env creado"
fi

echo ""
echo "=================================================="
echo "Siguientes pasos:"
echo "=================================================="
echo ""
echo "1. Configurar Gunicorn:"
echo "   sudo nano /etc/supervisor/conf.d/$NOMBRE_SERVICIO.conf"
echo ""
echo "2. Usar esta configuración de Gunicorn:"
cat << 'EOF'
[program:migrador-bd]
user=www-data
directory=/opt/migrador-bd
command=/opt/migrador-bd/venv/bin/gunicorn \
    --workers 4 \
    --worker-class eventlet \
    --bind 127.0.0.1:8000 \
    --timeout 300 \
    wsgi:app
autostart=true
autorestart=true
stderr_logfile=/var/log/migrador-bd.err.log
stdout_logfile=/var/log/migrador-bd.out.log
environment=PATH="/opt/migrador-bd/venv/bin"
EOF
echo ""
echo "3. Configurar Nginx (ver nginx_config.txt)"
echo "4. Iniciar el servicio:"
echo "   sudo supervisorctl reread"
echo "   sudo supervisorctl update"
echo "   sudo supervisorctl start migrador-bd"
echo ""
echo "5. Verificar estado:"
echo "   sudo supervisorctl status migrador-bd"
echo ""
echo "=================================================="
