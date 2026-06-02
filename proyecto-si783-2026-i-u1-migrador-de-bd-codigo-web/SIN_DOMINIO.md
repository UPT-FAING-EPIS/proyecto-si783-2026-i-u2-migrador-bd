# 🚀 DESPLIEGUE SIN DOMINIO (Solo con IP)

## ⚡ Esto es lo que necesitas hacer

### Tu Situación
- ✅ Tienes VPS Ubuntu
- ✅ Tienes IP (ej: 192.168.1.100)
- ❌ No tienes dominio (todavía)
- ❌ No tienes SSL (por ahora)

**¡Perfecto!** Funciona igual. Solo necesitas tu IP.

---

## 🎯 3 Opciones (Elige una)

### Opción 1️⃣: MEGA RÁPIDO (2 minutos) ⭐ RECOMENDADO

```bash
# 1. Conecta a tu VPS
ssh usuario@TU_IP_VPS

# 2. Ejecuta esto:
bash setup_produccion.sh 8000

# 3. ¡Listo! Tu app está en: http://TU_IP_VPS
```

**Eso es todo.** El script hace todo automáticamente.

---

### Opción 2️⃣: Rápido (5 minutos)

```bash
ssh usuario@TU_IP_VPS
bash quick_deploy.sh 8000

# Acceso: http://TU_IP_VPS
```

---

### Opción 3️⃣: Manual (10 pasos)

Ver archivo: `DEPLOY_CON_IP.md`

---

## 📋 Comandos Básicos Después

```bash
# Ver si está corriendo
sudo supervisorctl status migrador-bd

# Reiniciar
sudo supervisorctl restart migrador-bd

# Ver errores
sudo tail -f /var/log/migrador-bd-error.log

# Tu IP
hostname -I
```

---

## ❓ ¿Necesito mi IP?

Ejecuta en tu VPS:
```bash
hostname -I
```

O:
```bash
curl ifconfig.me
```

---

## 🎉 ¡Eso es todo!

- Despliegue: **2-5 minutos**
- Acceso: **http://TU_IP_VPS**
- Mantenimiento: **Cero** (Supervisor se encarga)

Cuando tengas dominio después, solo agregas la configuración SSL sin cambiar nada.

---

## 📞 ¿Preguntas?

Escribe tu IP o pregunta aquí 👇
