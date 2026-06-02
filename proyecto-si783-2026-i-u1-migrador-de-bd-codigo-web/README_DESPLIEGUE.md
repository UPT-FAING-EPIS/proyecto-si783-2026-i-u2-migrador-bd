# 🚀 REFERENCIA RÁPIDA - SIN DOMINIO

## Tu Comando (Copiar y Pegar)

```bash
ssh usuario@TU_IP_VPS
bash setup_produccion.sh 8000
```

Reemplaza `usuario` y `TU_IP_VPS` con tus datos reales.

**Ejemplo real:**
```bash
ssh root@192.168.1.100
bash setup_produccion.sh 8000
```

---

## Después de Ejecutar

Espera ~2 minutos y abre:
```
http://TU_IP_VPS
```

**Ejemplo:**
```
http://192.168.1.100
```

---

## Archivos Importantes

| Archivo | Qué Hace |
|---------|----------|
| `SIN_DOMINIO.md` | Instrucciones para IP |
| `DEPLOY_CON_IP.md` | Pasos manuales |
| `setup_produccion.sh` | Script automático |
| `nginx_migrador-bd.conf` | Config Nginx |

---

## Comandos Útiles

```bash
# Estado
sudo supervisorctl status migrador-bd

# Reiniciar
sudo supervisorctl restart migrador-bd

# Ver logs
sudo tail -f /var/log/migrador-bd-error.log
```

---

## Agregar Dominio Después

Cuando tengas dominio:

```bash
sudo apt-get install -y certbot python3-certbot-nginx
sudo certbot --nginx -d tu-dominio.com
```

Listo. No necesitas cambiar nada más.

---

## ¿Dudas?

1. ¿Cuál es mi IP? → `hostname -I` en tu VPS
2. ¿Por qué tarda? → Sistema instalando paquetes
3. ¿No funciona? → Ver logs: `sudo tail -f /var/log/migrador-bd-error.log`

---

**¡Listo en 2 minutos!** 🎉
