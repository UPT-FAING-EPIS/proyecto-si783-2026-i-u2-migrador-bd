#!/bin/bash

# ============================================================
# SCRIPT DE DESPLIEGUE ULTRA-RÁPIDO PARA UBUNTU
# ============================================================
# Descripción: Instala y configura MigradorBD en Ubuntu
# Uso: bash setup_produccion.sh
# ============================================================

set -e  # Salir si hay error

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Función para imprimir
print_header() {
    echo -e "\n${BLUE}➜ $1${NC}"
}

print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

# ============================================================
# INICIO
# ============================================================

echo -e "${BLUE}"
cat << "EOF"
╔═══════════════════════════════════════════════════════════╗
║         MIGRADOR BD - DESPLIEGUE EN PRODUCCIÓN            ║
║              Ubuntu 20.04 / 22.04 / 24.04                ║
╚═══════════════════════════════════════════════════════════╝
EOF
echo -e "${NC}"

# Variables
PUERTO=${1:-8000}
DIRECTORIO=${2:-/opt/migrador-bd}
USUARIO_SISTEMA="www-data"

print_header "Verificando permisos de sudo..."
if ! sudo -n true 2>/dev/null; then
    print_error "Se requieren permisos sudo"
    exit 1
fi
print_success "Permisos OK"

# ============================================================
# PASO 1: ACTUALIZAR SISTEMA
# ============================================================

print_header "1️⃣  Actualizando sistema..."
sudo apt-get update > /dev/null 2>&1
sudo apt-get upgrade -y > /dev/null 2>&1
print_success "Sistema actualizado"

# ============================================================
# PASO 2: INSTALAR DEPENDENCIAS
# ============================================================

print_header "2️⃣  Instalando dependencias..."
sudo apt-get install -y \
    python3 python3-pip python3-venv \
    nginx supervisor \
    curl wget git \
    build-essential \
    > /dev/null 2>&1
print_success "Dependencias instaladas"

# ============================================================
# PASO 3: PREPARAR DIRECTORIO
# ============================================================

print_header "3️⃣  Preparando directorio ($DIRECTORIO)..."
sudo mkdir -p "$DIRECTORIO"
sudo chown $USER:$USER "$DIRECTORIO"

if [ ! -f "$DIRECTORIO/run.py" ]; then
    print_error "No se encontró run.py en $DIRECTORIO"
    print_header "¿Copiaste los archivos del proyecto?"
    exit 1
fi
print_success "Directorio preparado"

cd "$DIRECTORIO"

# ============================================================
# PASO 4: CONFIGURAR PYTHON
# ============================================================

print_header "4️⃣  Configurando entorno Python..."

if [ ! -d "venv" ]; then
    python3 -m venv venv > /dev/null 2>&1
fi

source venv/bin/activate

pip install --upgrade pip setuptools wheel > /dev/null 2>&1

if [ -f "requirements.txt" ]; then
    pip install -r requirements.txt > /dev/null 2>&1
else
    pip install \
        flask flask-socketio flask-cors \
        python-dotenv werkzeug \
        pandas sqlalchemy \
        gunicorn eventlet \
        > /dev/null 2>&1
fi

print_success "Python configurado"

# ============================================================
# PASO 5: CREAR ARCHIVO .env
# ============================================================

print_header "5️⃣  Configurando variables de entorno..."

if [ ! -f ".env" ]; then
    SECRET=$(python3 -c 'import secrets; print(secrets.token_hex(32))')
    cat > .env << EOF
FLASK_ENV=production
FLASK_APP=run.py
HOST=127.0.0.1
PORT=5000
SECRET_KEY=$SECRET
EOF
    print_success "Archivo .env creado"
else
    print_success "Archivo .env ya existe"
fi

# ============================================================
# PASO 6: CONFIGURAR SUPERVISOR
# ============================================================

print_header "6️⃣  Configurando Supervisor (gestor de procesos)..."

sudo tee /etc/supervisor/conf.d/migrador-bd.conf > /dev/null << EOF
[program:migrador-bd]
user=$USUARIO_SISTEMA
directory=$DIRECTORIO
command=$DIRECTORIO/venv/bin/gunicorn \\
    --workers 4 \\
    --worker-class eventlet \\
    --bind 127.0.0.1:$PUERTO \\
    --timeout 300 \\
    --access-logfile - \\
    --error-logfile - \\
    wsgi:app

autostart=true
autorestart=true
startsecs=10
stopwaitsecs=10

stderr_logfile=/var/log/migrador-bd-error.log
stdout_logfile=/var/log/migrador-bd-access.log

environment=PATH="$DIRECTORIO/venv/bin",\\
    PYTHONUNBUFFERED=1,\\
    FLASK_ENV=production
EOF

sudo supervisorctl reread > /dev/null 2>&1
sudo supervisorctl update > /dev/null 2>&1
sleep 1

print_success "Supervisor configurado"

# ============================================================
# PASO 7: CONFIGURAR NGINX
# ============================================================

print_header "7️⃣  Configurando Nginx (servidor web)..."

sudo tee /etc/nginx/sites-available/migrador-bd > /dev/null << 'EOF'
upstream migrador_app {
    server 127.0.0.1:$PUERTO;
    keepalive 32;
}

server {
    listen 80 default_server;
    listen [::]:80 default_server;
    
    server_name _;
    client_max_body_size 500M;
    
    access_log /var/log/nginx/migrador-bd-access.log;
    error_log /var/log/nginx/migrador-bd-error.log;
    
    location / {
        proxy_pass http://migrador_app;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_read_timeout 300s;
        proxy_connect_timeout 300s;
        proxy_send_timeout 300s;
    }
    
    location /socket.io {
        proxy_pass http://migrador_app/socket.io;
        proxy_http_version 1.1;
        proxy_buffering off;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "Upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
}
EOF

# Reemplazar el puerto en la configuración
sed -i "s|\$PUERTO|$PUERTO|g" /etc/nginx/sites-available/migrador-bd

# Habilitar sitio
sudo ln -sf /etc/nginx/sites-available/migrador-bd /etc/nginx/sites-enabled/ 2>/dev/null
sudo rm -f /etc/nginx/sites-enabled/default 2>/dev/null

# Verificar configuración
if ! sudo nginx -t > /dev/null 2>&1; then
    print_error "Error en configuración de Nginx"
    sudo nginx -t
    exit 1
fi

sudo systemctl restart nginx > /dev/null 2>&1
print_success "Nginx configurado"

# ============================================================
# PASO 8: PERMISOS DE ARCHIVOS
# ============================================================

print_header "8️⃣  Configurando permisos..."
sudo chown -R $USUARIO_SISTEMA:$USUARIO_SISTEMA "$DIRECTORIO/uploads" 2>/dev/null || true
sudo chmod -R 755 "$DIRECTORIO/uploads" 2>/dev/null || true
print_success "Permisos configurados"

# ============================================================
# PASO 9: INICIAR SERVICIO
# ============================================================

print_header "9️⃣  Iniciando servicio..."
sudo supervisorctl start migrador-bd > /dev/null 2>&1
sleep 2

# Verificar estado
if sudo supervisorctl status migrador-bd | grep -q "RUNNING"; then
    print_success "Servicio iniciado correctamente"
else
    print_error "El servicio no está corriendo"
    print_header "Viendo logs..."
    sudo supervisorctl tail migrador-bd stderr
    exit 1
fi

# ============================================================
# FIN
# ============================================================

echo -e "\n${GREEN}╔═══════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║         ✓ ¡INSTALACIÓN COMPLETADA!                        ║${NC}"
echo -e "${GREEN}╚═══════════════════════════════════════════════════════════╝${NC}\n"

echo -e "${BLUE}📍 Acceso:${NC}"
echo "   URL: http://$(hostname -I | awk '{print $1}')"
echo "   Puerto interno: $PUERTO"
echo "   Directorio: $DIRECTORIO"

echo -e "\n${BLUE}📋 Comandos útiles:${NC}"
echo "   Ver estado:    sudo supervisorctl status migrador-bd"
echo "   Reiniciar:     sudo supervisorctl restart migrador-bd"
echo "   Logs Gunicorn: sudo tail -f /var/log/migrador-bd-error.log"
echo "   Logs Nginx:    sudo tail -f /var/log/nginx/migrador-bd-error.log"

echo -e "\n${BLUE}🔒 SSL/HTTPS (Let's Encrypt):${NC}"
echo "   sudo apt-get install -y certbot python3-certbot-nginx"
echo "   sudo certbot --nginx -d tu-dominio.com"

echo -e "\n${BLUE}🔄 Cambiar puerto:${NC}"
echo "   1. Editar: sudo nano /etc/supervisor/conf.d/migrador-bd.conf"
echo "   2. Cambiar --bind 127.0.0.1:$PUERTO a --bind 127.0.0.1:NUEVO_PUERTO"
echo "   3. Ejecutar: sudo supervisorctl restart migrador-bd"

echo -e "\n${GREEN}La aplicación estará lista en ~30 segundos${NC}"
echo -e "${GREEN}¡Tu aplicación está desplegada en Ubuntu! 🎉${NC}\n"
