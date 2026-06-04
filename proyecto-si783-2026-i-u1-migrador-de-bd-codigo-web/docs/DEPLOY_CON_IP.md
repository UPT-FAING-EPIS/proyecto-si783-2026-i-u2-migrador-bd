# 🚀 Despliegue en Ubuntu con IP (Sin Dominio)

## ✅ Opción Recomendada: Script Automático (2 minutos)

### Paso 1: Conecta a tu VPS
```bash
ssh usuario@TU_IP_VPS
```

### Paso 2: Ejecuta el script
```bash
wget https://raw.githubusercontent.com/tu-repo/setup_produccion.sh
bash setup_produccion.sh 8000 /opt/migrador-bd
```

**Listo!** Tu app estará en: `http://TU_IP_VPS`

---

## 🔧 Despliegue Manual (Si lo prefieres)

### Paso 1: Conectar y actualizar
```bash
ssh usuario@TU_IP_VPS
sudo apt-get update && sudo apt-get upgrade -y
```

### Paso 2: Instalar lo necesario
```bash
sudo apt-get install -y python3 python3-pip python3-venv nginx supervisor
```

### Paso 3: Preparar proyecto
```bash
sudo mkdir -p /opt/migrador-bd
sudo chown $USER:$USER /opt/migrador-bd
cd /opt/migrador-bd

# Copiar archivos (en tu máquina local):
# scp -r ./* usuario@TU_IP_VPS:/opt/migrador-bd/
```

### Paso 4: Configurar Python
```bash
cd /opt/migrador-bd
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
pip install gunicorn eventlet
```

### Paso 5: Crear Supervisor
```bash
sudo nano /etc/supervisor/conf.d/migrador-bd.conf
```

Pega esto:
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
stdout_logfile=/var/log/migrador-bd-access.log
environment=PATH="/opt/migrador-bd/venv/bin",FLASK_ENV=production
```

Luego:
```bash
sudo supervisorctl reread
sudo supervisorctl update
sudo supervisorctl start migrador-bd
```

### Paso 6: Configurar Nginx para IP
```bash
sudo nano /etc/nginx/sites-available/migrador-bd
```

**Copia esto exactamente:**
```nginx
upstream migrador_app {
    server 127.0.0.1:8000;
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
        proxy_read_timeout 300s;
    }
    
    location /socket.io {
        proxy_pass http://migrador_app/socket.io;
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

### Paso 7: Verificar
```bash
sudo supervisorctl status migrador-bd
sudo tail -f /var/log/migrador-bd-error.log
```

---

## 🎯 Acceder a tu App

Abre tu navegador:
```
http://TU_IP_VPS
```

Reemplaza `TU_IP_VPS` con tu dirección IP real.

**Ejemplo:** `http://192.168.1.100`

---

## 🔄 Cambiar Puerto

Si quieres usar otro puerto (ej. 8080):

### En Supervisor:
```bash
sudo nano /etc/supervisor/conf.d/migrador-bd.conf
# Cambiar "bind 127.0.0.1:8000" a "bind 127.0.0.1:8080"
sudo supervisorctl restart migrador-bd
```

### En Nginx:
```bash
sudo nano /etc/nginx/sites-available/migrador-bd
# Cambiar "server 127.0.0.1:8000;" a "server 127.0.0.1:8080;"
sudo nginx -t
sudo systemctl restart nginx
```

Luego accede a: `http://TU_IP_VPS:8080`

---

## 📋 Comandos Útiles

```bash
# Ver estado
sudo supervisorctl status migrador-bd

# Reiniciar
sudo supervisorctl restart migrador-bd

# Ver logs
sudo tail -f /var/log/migrador-bd-error.log

# Ver tu IP
hostname -I
```

---

## 🔐 Firewall

```bash
# Permitir SSH
sudo ufw allow 22/tcp

# Permitir HTTP
sudo ufw allow 80/tcp

# Permitir puerto personalizado (ej. 8080)
sudo ufw allow 8080/tcp

# Activar firewall
sudo ufw enable
```

---

## 🔒 SSL/HTTPS Después (Opcional)

Cuando obtengas un dominio:

```bash
sudo apt-get install -y certbot python3-certbot-nginx
sudo certbot --nginx -d tu-dominio.com
```

---

## ❓ ¿Cuál es mi IP?

En tu VPS ejecuta:
```bash
hostname -I
```

O si está en la nube:
```bash
curl ifconfig.me
```

---

## 🎉 ¡Listo!

Tu aplicación funciona sin dominio, solo con tu IP.

Cuando tengas dominio, podrás agregarlo sin cambiar nada de la configuración actual.

**¿Necesitas ayuda?** Escribe tu IP aquí y te doy instrucciones específicas 👇
