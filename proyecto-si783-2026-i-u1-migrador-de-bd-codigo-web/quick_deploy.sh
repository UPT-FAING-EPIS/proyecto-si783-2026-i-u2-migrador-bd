#!/bin/bash

# Script rápido de instalación (versión minimalista)
# Uso: bash quick_deploy.sh

set -e

PUERTO=${1:-8000}
DIRECTORIO=${2:-/opt/migrador-bd}

echo "🚀 Instalación rápida de MigradorBD"
echo "Puerto: $PUERTO | Directorio: $DIRECTORIO"
echo ""

# 1. Dependencias
echo "📦 Instalando dependencias..."
sudo apt-get update > /dev/null 2>&1
sudo apt-get install -y python3 python3-pip python3-venv nginx supervisor > /dev/null 2>&1

# 2. Crear directorio
echo "📁 Preparando directorio..."
sudo mkdir -p "$DIRECTORIO"
sudo chown $USER:$USER "$DIRECTORIO"
cd "$DIRECTORIO"

# 3. Venv y dependencias
echo "🐍 Configurando Python..."
python3 -m venv venv > /dev/null 2>&1
source venv/bin/activate
pip install -q --upgrade pip
pip install -q -r requirements.txt 2>/dev/null || pip install -q flask flask-socketio python-dotenv gunicorn eventlet

# 4. Crear .env
if [ ! -f .env ]; then
    echo "⚙️ Configurando variables..."
    cat > .env << EOF
FLASK_ENV=production
HOST=127.0.0.1
PORT=5000
SECRET_KEY=$(python3 -c 'import secrets; print(secrets.token_hex(32))')
EOF
fi

# 5. Supervisor
echo "🔧 Configurando Supervisor..."
sudo tee /etc/supervisor/conf.d/migrador-bd.conf > /dev/null << EOF
[program:migrador-bd]
user=www-data
directory=$DIRECTORIO
command=$DIRECTORIO/venv/bin/gunicorn --workers 4 --worker-class eventlet --bind 127.0.0.1:$PUERTO --timeout 300 wsgi:app
autostart=true
autorestart=true
stderr_logfile=/var/log/migrador-bd.err.log
stdout_logfile=/var/log/migrador-bd.out.log
environment=PATH="$DIRECTORIO/venv/bin",FLASK_ENV=production
EOF

sudo supervisorctl reread > /dev/null 2>&1
sudo supervisorctl update > /dev/null 2>&1

# 6. Nginx
echo "🌐 Configurando Nginx..."
sudo tee /etc/nginx/sites-available/migrador-bd > /dev/null << EOF
upstream app {
    server 127.0.0.1:$PUERTO;
}

server {
    listen 80;
    server_name _;
    client_max_body_size 500M;

    location / {
        proxy_pass http://app;
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_read_timeout 300s;
    }

    location /socket.io {
        proxy_pass http://app/socket.io;
        proxy_http_version 1.1;
        proxy_buffering off;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection "Upgrade";
        proxy_set_header Host \$host;
    }
}
EOF

sudo ln -sf /etc/nginx/sites-available/migrador-bd /etc/nginx/sites-enabled/ 2>/dev/null
sudo rm -f /etc/nginx/sites-enabled/default 2>/dev/null
sudo nginx -t > /dev/null 2>&1
sudo systemctl restart nginx > /dev/null 2>&1

# 7. Iniciar servicio
echo "🚀 Iniciando servicio..."
sudo supervisorctl start migrador-bd > /dev/null 2>&1
sleep 2

# 8. Resultado
echo ""
echo "✅ ¡Instalación completada!"
echo ""
echo "📍 Acceso:"
echo "   URL: http://tu-ip"
echo "   Puerto: $PUERTO (interno)"
echo ""
echo "📋 Comandos útiles:"
echo "   Estado:     sudo supervisorctl status migrador-bd"
echo "   Reiniciar:  sudo supervisorctl restart migrador-bd"
echo "   Logs:       sudo tail -f /var/log/migrador-bd.err.log"
echo ""
echo "⏱️  La app estará lista en ~10 segundos..."
