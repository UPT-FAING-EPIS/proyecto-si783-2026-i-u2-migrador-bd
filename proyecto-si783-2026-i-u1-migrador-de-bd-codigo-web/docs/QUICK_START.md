# 🚀 Despliegue en Ubuntu - Guía Rápida (5 pasos)

## 🎯 Tienes 2 Casos

### 1️⃣ SIN DOMINIO (Solo con IP) ⭐ Más Fácil
→ Lee: **`SIN_DOMINIO.md`**

```bash
ssh usuario@TU_IP_VPS
bash setup_produccion.sh 8000
# Acceso: http://TU_IP_VPS
```

### 2️⃣ CON DOMINIO (Para después)
→ Lee: **`DEPLOY_CON_IP.md`** o **`DEPLOY_UBUNTU.md`**

---

## Requisitos
- VPS Ubuntu 20.04+
- Acceso SSH
- ~2GB RAM, 20GB disco

---

## Opción A: Instalación Automática (2 minutos)

```bash
# 1. Conecta a tu VPS
ssh usuario@tu-vps.com

# 2. Descarga y ejecuta
bash <(curl -s https://tu-url.com/quick_deploy.sh) 8000

# ¡Listo! Tu app está en http://tu-vps.com
```

**Parámetros opcionales:**
```bash
bash quick_deploy.sh 8000 /opt/migrador-bd
# Puerto 8000, directorio /opt/migrador-bd
```

---

## Opción B: Instalación Manual (10 pasos)

### Paso 1: Conectar y actualizar
```bash
ssh usuario@tu-vps.com
sudo apt-get update && sudo apt-get upgrade -y
```

### Paso 2: Instalar dependencias
```bash
sudo apt-get install -y python3 python3-pip python3-venv nginx supervisor
```

### Paso 3: Crear directorio
```bash
sudo mkdir -p /opt/migrador-bd
sudo chown $USER:$USER /opt/migrador-bd
cd /opt/migrador-bd
```

### Paso 4: Copiar proyecto
En tu máquina local:
```bash
scp -r ./* usuario@tu-vps.com:/opt/migrador-bd/
```

### Paso 5: Crear entorno Python
```bash
cd /opt/migrador-bd
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
pip install gunicorn eventlet
```

### Paso 6: Crear archivo .env
```bash
cat > .env << 'EOF'
FLASK_ENV=production
HOST=127.0.0.1
PORT=5000
SECRET_KEY=tu-secret-key-aqui
EOF
```

### Paso 7: Configurar Supervisor (Gunicorn)
```bash
sudo nano /etc/supervisor/conf.d/migrador-bd.conf
```

Copia esto:
```ini
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
stderr_logfile=/var/log/migrador-bd-error.log
environment=PATH="/opt/migrador-bd/venv/bin",FLASK_ENV=production
```

Luego:
```bash
sudo supervisorctl reread
sudo supervisorctl update
sudo supervisorctl start migrador-bd
```

### Paso 8: Configurar Nginx
```bash
sudo nano /etc/nginx/sites-available/migrador-bd
```

Copia esto:
```nginx
upstream app {
    server 127.0.0.1:8000;
}

server {
    listen 80;
    server_name _;
    client_max_body_size 500M;

    location / {
        proxy_pass http://app;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_read_timeout 300s;
    }

    location /socket.io {
        proxy_pass http://app/socket.io;
        proxy_http_version 1.1;
        proxy_buffering off;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "Upgrade";
        proxy_set_header Host $host;
    }
}
```

Luego:
```bash
sudo ln -s /etc/nginx/sites-available/migrador-bd /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default
sudo nginx -t
sudo systemctl restart nginx
```

### Paso 9: Configurar firewall (opcional pero recomendado)
```bash
sudo ufw allow 22/tcp
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw enable
```

### Paso 10: Verificar estado
```bash
sudo supervisorctl status migrador-bd
sudo tail -f /var/log/migrador-bd-error.log
```

---

## Cambiar el Puerto

Si quieres usar otro puerto (ej. 8080):

### En Supervisor:
```bash
# Cambiar 127.0.0.1:8000 a 127.0.0.1:8080
sudo nano /etc/supervisor/conf.d/migrador-bd.conf
# Cambiar la línea "bind" de 8000 a 8080
sudo supervisorctl restart migrador-bd
```

### En Nginx:
```bash
sudo nano /etc/nginx/sites-available/migrador-bd
# Cambiar "server 127.0.0.1:8000;" a "server 127.0.0.1:8080;"
sudo nginx -t
sudo systemctl restart nginx
```

---

## Comandos Útiles

```bash
# Ver estado
sudo supervisorctl status migrador-bd

# Reiniciar
sudo supervisorctl restart migrador-bd

# Ver logs
sudo tail -f /var/log/migrador-bd-error.log
sudo tail -f /var/log/nginx/error.log

# Detener
sudo supervisorctl stop migrador-bd

# Iniciar de nuevo
sudo supervisorctl start migrador-bd

# Verificar puertos
sudo netstat -tlnp | grep python
sudo netstat -tlnp | grep nginx
```

---

## SSL/HTTPS (Let's Encrypt)

```bash
# Instalar certbot
sudo apt-get install -y certbot python3-certbot-nginx

# Crear certificado (reemplaza tu-dominio.com)
sudo certbot certonly --nginx -d tu-dominio.com

# El certificado se guardará en:
# /etc/letsencrypt/live/tu-dominio.com/fullchain.pem
# /etc/letsencrypt/live/tu-dominio.com/privkey.pem

# Renovar certificado (ejecutar cada 3 meses o agregar a cron)
sudo certbot renew
```

Luego actualiza Nginx con:
```nginx
ssl_certificate /etc/letsencrypt/live/tu-dominio.com/fullchain.pem;
ssl_certificate_key /etc/letsencrypt/live/tu-dominio.com/privkey.pem;
```

---

## Solucionar Problemas

### ❌ "Connection refused"
```bash
# Verificar si Gunicorn está corriendo
sudo supervisorctl status migrador-bd

# Si no, ver error
sudo supervisorctl tail migrador-bd stderr
```

### ❌ "Permission denied en uploads"
```bash
sudo chown -R www-data:www-data /opt/migrador-bd/uploads
sudo chmod 755 /opt/migrador-bd/uploads
```

### ❌ WebSocket no funciona
Asegúrate que Nginx tiene:
```nginx
proxy_set_header Upgrade $http_upgrade;
proxy_set_header Connection "upgrade";
```

### ❌ Nginx no inicia
```bash
sudo nginx -t  # Ver error
```

---

## Próximos Pasos

1. **Dominio**: Apunta tu dominio al IP del VPS
2. **SSL**: Configura HTTPS con Let's Encrypt
3. **Backups**: Backup automático de la base de datos
4. **Monitoreo**: Configura alertas

---

## Soporte

Para más información, ver `DEPLOY_UBUNTU.md` en el proyecto.

¡Tu app estará lista en minutos! 🎉
