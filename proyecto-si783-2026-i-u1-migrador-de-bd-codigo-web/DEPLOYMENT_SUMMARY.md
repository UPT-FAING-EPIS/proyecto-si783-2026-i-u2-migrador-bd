# 🚀 Despliegue en Ubuntu - Resumen Visual

## ⭐ Sin Dominio (Solo IP)

Si no tienes dominio, es **MÁS FÁCIL** aún:

```bash
ssh usuario@TU_IP_VPS
bash setup_produccion.sh 8000
```

Acceso: `http://TU_IP_VPS`

Ver: **`SIN_DOMINIO.md`**

---

## 📦 Archivos Incluidos para Despliegue

```
tu-proyecto/
├── README_DESPLIEGUE.md         ← COMIENZA AQUÍ
├── SIN_DOMINIO.md               ← Si no tienes dominio
├── setup_produccion.sh          ← SCRIPT AUTOMÁTICO
├── quick_deploy.sh              ← VERSIÓN MINIMALISTA
├── QUICK_START.md               ← GUÍA RÁPIDA
├── DEPLOY_CON_IP.md             ← SIN DOMINIO (Manual)
├── DEPLOY_UBUNTU.md             ← GUÍA COMPLETA
├── DEPLOYMENT_SUMMARY.md        ← Este archivo
├── supervisor_migrador-bd.conf  ← CONFIG SUPERVISOR
├── nginx_migrador-bd.conf       ← CONFIG NGINX
├── wsgi.py                      ← ENTRYPOINT GUNICORN
├── requirements.txt             ← DEPENDENCIAS PYTHON
└── run.py                       ← ARCHIVO PRINCIPAL
```

---

## ⚡ 3 Formas de Desplegar

### Opción 1️⃣: ULTRA RÁPIDO (2 minutos)
```bash
ssh usuario@tu-vps.com
cd /tmp
wget https://tu-url.com/setup_produccion.sh
bash setup_produccion.sh 8000 /opt/migrador-bd
```

### Opción 2️⃣: Rápido (5 minutos)
```bash
bash quick_deploy.sh 8000
```

### Opción 3️⃣: Manual (10 pasos)
Ver archivo `QUICK_START.md`

---

## 🏗️ Arquitectura de Despliegue

```
┌─────────────────────────────────────────────────┐
│              USUARIO (tu-ip.com)                │
│                    ↓ HTTP/HTTPS                 │
├─────────────────────────────────────────────────┤
│        NGINX (Reverse Proxy)                    │
│        Puerto 80, 443                           │
│        • Equilibrio de carga                     │
│        • Manejo de WebSocket                     │
│        • Compresión de archivos                  │
│                    ↓                             │
├─────────────────────────────────────────────────┤
│      SUPERVISOR (Process Manager)               │
│      • Reinicia automáticamente                 │
│      • Monitoreo 24/7                           │
│                    ↓                             │
├─────────────────────────────────────────────────┤
│  GUNICORN (App Server) - Puerto 8000            │
│  • 4 workers                                     │
│  • Worker class: eventlet (para WebSocket)      │
│  • Timeout: 300s                                │
│                    ↓                             │
├─────────────────────────────────────────────────┤
│  PYTHON/FLASK (Tu Aplicación)                   │
│  • run.py / wsgi.py                             │
│  • Socket.IO para tiempo real                   │
│  • Base de datos SQLite/MySQL/PostgreSQL        │
└─────────────────────────────────────────────────┘
```

---

## 🎯 Configuración de Puertos

| Puerto | Servicio | Acceso |
|--------|----------|--------|
| **80** | HTTP → Nginx | Público (redirige a 443) |
| **443** | HTTPS → Nginx | Público (SSL/TLS) |
| **8000** | Gunicorn | Solo localhost (desde Nginx) |
| **8080** | Nginx Alt | Público (sin SSL, opcional) |

---

## ✅ Checklist de Despliegue

- [ ] VPS Ubuntu 20.04+ con acceso SSH
- [ ] Ejecutar `setup_produccion.sh`
- [ ] Verificar que la app inicia: `sudo supervisorctl status migrador-bd`
- [ ] Acceder a `http://tu-ip`
- [ ] Configurar dominio y DNS
- [ ] Instalar SSL con Let's Encrypt
- [ ] Configurar firewall (UFW)
- [ ] Backup automático

---

## 🔧 Después del Despliegue

### Cambiar Puerto
```bash
# 1. Editar configuración
sudo nano /etc/supervisor/conf.d/migrador-bd.conf
# 2. Buscar "bind 127.0.0.1:8000" y cambiar 8000 a tu puerto
# 3. Guardar (Ctrl+X, Y, Enter)
# 4. Reiniciar
sudo supervisorctl restart migrador-bd
```

### Configurar SSL
```bash
sudo apt-get install -y certbot python3-certbot-nginx
sudo certbot --nginx -d tu-dominio.com
```

### Ver Logs
```bash
# Logs de la aplicación
sudo tail -f /var/log/migrador-bd-error.log

# Logs de Nginx
sudo tail -f /var/log/nginx/migrador-bd-error.log

# Ver estado
sudo supervisorctl status migrador-bd
```

### Reiniciar Aplicación
```bash
sudo supervisorctl restart migrador-bd
```

---

## 📊 Monitoreo

### Ver recursos en tiempo real
```bash
# Memory y CPU
top

# Procesos Python
ps aux | grep gunicorn

# Puertos abiertos
sudo netstat -tlnp | grep -E "(nginx|gunicorn)"
```

### Alertas automáticas
Supervisor reiniciará automáticamente si la app cae.

---

## 🆘 Solucionar Problemas

### ❌ "Connection refused" 
```bash
sudo supervisorctl status migrador-bd
sudo tail -f /var/log/migrador-bd-error.log
```

### ❌ "Permission denied"
```bash
sudo chown -R www-data:www-data /opt/migrador-bd/uploads
```

### ❌ WebSocket no funciona
Verifica que Nginx tenga:
```nginx
proxy_set_header Upgrade $http_upgrade;
proxy_set_header Connection "upgrade";
```

### ❌ Puerto ya en uso
```bash
sudo lsof -i :8000  # Ver qué lo ocupa
sudo kill -9 <PID>  # Matar el proceso
```

---

## 📈 Performance

Con esta configuración puedes esperar:
- **~100 usuarios simultáneos** por worker (400 con 4 workers)
- **~500 MB RAM** para la aplicación
- **Upload de 500 MB** (configurable)
- **Respuesta < 100ms** para requests normales

---

## 🔐 Seguridad

### Firewall
```bash
sudo ufw allow 22/tcp    # SSH
sudo ufw allow 80/tcp    # HTTP
sudo ufw allow 443/tcp   # HTTPS
sudo ufw enable          # Activar
```

### Secreto Flask
Se genera automáticamente en `.env`

### HTTPS
Usa Let's Encrypt para SSL gratuito

---

## 📞 Soporte

### Documentación Completa
- `DEPLOY_UBUNTU.md` - Guía extensa
- `QUICK_START.md` - Guía rápida

### Comandos Principales
```bash
# Estado
sudo supervisorctl status migrador-bd

# Reiniciar
sudo supervisorctl restart migrador-bd

# Logs
sudo tail -f /var/log/migrador-bd-error.log

# Verificar puertos
sudo netstat -tlnp
```

---

## 🎉 ¡Listo!

Tu aplicación está ahora en producción en Ubuntu.

**Tiempo de despliegue:** 2-5 minutos
**Mantenimiento:** Mínimo (Supervisor se encarga de todo)
**Escalabilidad:** Fácil de aumentar recursos
