# Guía de Despliegue en Ubuntu (VPS)

## Requisitos
- Ubuntu 20.04 LTS o superior
- Acceso SSH a tu VPS
- Dominio (opcional, pero recomendado)

## Opción 1: Despliegue Automático (Recomendado)

### Paso 1: Descarga el script
```bash
# En tu VPS
cd /tmp
wget https://tu-dominio.com/deploy_ubuntu.sh
chmod +x deploy_ubuntu.sh
```

O copia el archivo `deploy_ubuntu.sh` a tu VPS:
```bash
scp deploy_ubuntu.sh usuario@tu-vps.com:/tmp/
ssh usuario@tu-vps.com
cd /tmp && chmod +x deploy_ubuntu.sh
```

### Paso 2: Ejecuta el script
```bash
sudo ./deploy_ubuntu.sh 8000 www-data /opt/migrador-bd
```

Parámetros:
- `8000`: Puerto interno para Gunicorn
- `www-data`: Usuario que ejecutará el servicio
- `/opt/migrador-bd`: Directorio de instalación

### Paso 3: Configura Supervisor
```bash
sudo nano /etc/supervisor/conf.d/migrador-bd.conf
```

Copia el contenido de `supervisor_migrador-bd.conf` (incluido en el proyecto).

Luego ejecuta:
```bash
sudo supervisorctl reread
sudo supervisorctl update
sudo supervisorctl start migrador-bd
```

### Paso 4: Configura Nginx
```bash
sudo nano /etc/nginx/sites-available/migrador-bd
```

Copia el contenido de `nginx_migrador-bd.conf` y reemplaza:
- `tu-dominio.com` con tu dominio real
- Los puertos según lo que necesites

Luego:
```bash
sudo ln -s /etc/nginx/sites-available/migrador-bd /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

### Paso 5: Configurar SSL (HTTPS)
```bash
sudo apt-get install certbot python3-certbot-nginx -y
sudo certbot certonly --webroot -w /var/www/certbot -d tu-dominio.com
```

---

## Opción 2: Despliegue Manual

### Paso 1: Conectate por SSH
```bash
ssh usuario@tu-vps.com
```

### Paso 2: Instalar dependencias
```bash
sudo apt-get update
sudo apt-get upgrade -y
sudo apt-get install -y python3 python3-pip python3-venv nginx supervisor curl git
```

### Paso 3: Crear directorio del proyecto
```bash
sudo mkdir -p /opt/migrador-bd
sudo chown $USER:$USER /opt/migrador-bd
cd /opt/migrador-bd
```

### Paso 4: Descargar el proyecto
```bash
# Opción A: Git (si tienes repositorio)
git clone https://tu-repo.git .

# Opción B: Copiar archivos locales
# En tu máquina local:
scp -r ./* usuario@tu-vps.com:/opt/migrador-bd/
```

### Paso 5: Crear entorno virtual
```bash
cd /opt/migrador-bd
python3 -m venv venv
source venv/bin/activate
```

### Paso 6: Instalar dependencias Python
```bash
pip install --upgrade pip
pip install -r requirements.txt
pip install gunicorn eventlet
```

### Paso 7: Crear archivo .env
```bash
cat > .env << 'EOF'
FLASK_ENV=production
FLASK_APP=run.py
HOST=127.0.0.1
PORT=5000
SECRET_KEY=$(python3 -c 'import secrets; print(secrets.token_hex(32))')
EOF
```

### Paso 8: Configurar Supervisor
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
environment=PATH="/opt/migrador-bd/venv/bin",PYTHONUNBUFFERED=1,FLASK_ENV=production
```

Luego:
```bash
sudo supervisorctl reread
sudo supervisorctl update
sudo supervisorctl start migrador-bd
```

### Paso 9: Configurar Nginx
```bash
sudo nano /etc/nginx/sites-available/migrador-bd
```

Pega el contenido de `nginx_migrador-bd.conf` y personaliza:

Luego:
```bash
sudo ln -s /etc/nginx/sites-available/migrador-bd /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

---

## Comandos Útiles

### Ver estado del servicio
```bash
sudo supervisorctl status migrador-bd
```

### Reiniciar la aplicación
```bash
sudo supervisorctl restart migrador-bd
```

### Ver logs
```bash
sudo tail -f /var/log/migrador-bd-error.log
sudo tail -f /var/log/migrador-bd-access.log
```

### Ver logs de Nginx
```bash
sudo tail -f /var/log/nginx/migrador-bd-access.log
sudo tail -f /var/log/nginx/migrador-bd-error.log
```

### Verificar que Gunicorn está escuchando
```bash
sudo netstat -tlnp | grep 8000
```

### Verificar que Nginx está correcto
```bash
sudo nginx -t
```

---

## Puertos Disponibles

- **8000** (interno): Gunicorn (solo desde localhost)
- **80** (externo): HTTP → Nginx (redirige a 443)
- **443** (externo): HTTPS → Nginx
- **8080** (externo - opcional): HTTP sin SSL (desarrollo)

---

## Solucionar Problemas

### Problema: "Permission denied" al subir archivos
```bash
sudo chown -R www-data:www-data /opt/migrador-bd/uploads
sudo chmod -R 755 /opt/migrador-bd/uploads
```

### Problema: Gunicorn no inicia
```bash
# Ver error específico
cd /opt/migrador-bd
source venv/bin/activate
gunicorn wsgi:app
```

### Problema: SSL no funciona
```bash
# Renovar certificado
sudo certbot renew

# O crear uno nuevo
sudo certbot certonly --nginx -d tu-dominio.com
```

### Problema: WebSocket no funciona
Asegurate de que:
1. Nginx tiene `proxy_set_header Upgrade $http_upgrade;`
2. Gunicorn usa `--worker-class eventlet`
3. No hay proxy inverso bloqueando WebSocket

---

## Monitoreo y Mantenimiento

### Configurar reinicio automático de servidor
```bash
# Agregar a crontab
sudo crontab -e

# Agregar línea:
0 3 * * * /usr/sbin/service supervisor restart
```

### Ver uso de recursos
```bash
# Ver procesos de Python
ps aux | grep gunicorn

# Ver memoria
free -h

# Ver uso de CPU
top
```

### Hacer backup de la aplicación
```bash
sudo tar -czf /backups/migrador-bd-$(date +%Y%m%d).tar.gz /opt/migrador-bd/
```

---

## Actualizar la aplicación

```bash
cd /opt/migrador-bd
git pull origin main  # Si usas Git
# O copia los archivos nuevos manualmente

source venv/bin/activate
pip install -r requirements.txt  # En caso de nuevas dependencias

sudo supervisorctl restart migrador-bd
```

---

## Configuración de Firewall (UFW)

```bash
# Permitir SSH
sudo ufw allow 22/tcp

# Permitir HTTP
sudo ufw allow 80/tcp

# Permitir HTTPS
sudo ufw allow 443/tcp

# Permitir puerto 8080 (opcional)
sudo ufw allow 8080/tcp

# Activar firewall
sudo ufw enable
```

---

## Siguiente Paso

Una vez desplegado, accede a:
- **HTTPS**: `https://tu-dominio.com`
- **HTTP**: `http://tu-dominio.com` (redirige a HTTPS)
- **Puerto 8080**: `http://tu-dominio.com:8080`

¡Listo! Tu aplicación está desplegada en Ubuntu. 🎉
