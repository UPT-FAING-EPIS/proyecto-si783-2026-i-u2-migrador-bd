#!/bin/bash

echo "=== DESPLIEGUE DE MIGRADORBD EN VPS LINUX ==="

# Actualizar sistema
sudo apt update && sudo apt upgrade -y

# Instalar dependencias del sistema
sudo apt install -y python3 python3-pip python3-venv nginx git

# Crear directorio del proyecto
sudo mkdir -p /var/www/migradorbd
sudo chown $USER:$USER /var/www/migradorbd

# Clonar o copiar el proyecto
cd /var/www/migradorbd
git clone https://github.com/UPT-FAING-EPIS/proyecto-si783-2026-i-u1-migrador-de-bd.git .

# Crear entorno virtual
python3 -m venv venv
source venv/bin/activate

# Instalar dependencias
pip install --upgrade pip
pip install -r requirements_web.txt
pip install gunicorn eventlet

# Configurar Nginx
sudo cp despliegue/nginx_config /etc/nginx/sites-available/migradorbd
sudo ln -s /etc/nginx/sites-available/migradorbd /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx

# Crear servicio systemd para Gunicorn
sudo tee /etc/systemd/system/migradorbd.service << EOF
[Unit]
Description=MigradorBD Web Application
After=network.target

[Service]
User=$USER
Group=www-data
WorkingDirectory=/var/www/migradorbd
Environment="PATH=/var/www/migradorbd/venv/bin"
ExecStart=/var/www/migradorbd/venv/bin/gunicorn --worker-class eventlet -w 1 wsgi:app -b 127.0.0.1:8000

[Install]
WantedBy=multi-user.target
EOF

# Iniciar servicio
sudo systemctl daemon-reload
sudo systemctl start migradorbd
sudo systemctl enable migradorbd

echo "=== DESPLIEGUE COMPLETADO ==="
echo "Accede a: http://migradorbd.net"