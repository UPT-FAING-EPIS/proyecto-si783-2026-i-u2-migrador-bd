#!/bin/bash
# =====================================================
#  update_vps.sh  —  Actualizar MigradorBD en el VPS
#  Ejecutar DIRECTAMENTE en el VPS:
#      bash /opt/migrador-bd/despliegue/update_vps.sh
#  O desde Windows via SSH:
#      ssh root@207.180.218.158 'bash /opt/migrador-bd/despliegue/update_vps.sh'
# =====================================================

set -e

DIRECTORIO="/opt/migrador-bd"
PROGRAMA_SUPERVISOR="migrador-bd"

echo ""
echo "======================================================"
echo "   ACTUALIZACION MigradorBD en VPS"
echo "======================================================"
echo ""

# ── 1. Git pull ────────────────────────────────────────
echo "[1/4] Obteniendo cambios del repositorio..."
cd "$DIRECTORIO"
git fetch origin
git pull origin main 2>/dev/null || git pull origin master 2>/dev/null
echo "      OK"

# ── 2. Instalar dependencias si cambiaron ──────────────
echo "[2/4] Revisando dependencias..."
if [ -f "$DIRECTORIO/venv/bin/activate" ]; then
    source "$DIRECTORIO/venv/bin/activate"
    pip install -q -r "$DIRECTORIO/requirements_web.txt" 2>/dev/null \
        || pip install -q -r "$DIRECTORIO/requirements.txt" 2>/dev/null \
        || true
    echo "      Dependencias OK"
else
    echo "      venv no encontrado, saltando..."
fi

# ── 3. Reiniciar supervisor ────────────────────────────
echo "[3/4] Reiniciando Supervisor ($PROGRAMA_SUPERVISOR)..."
sudo supervisorctl reread  > /dev/null 2>&1 || true
sudo supervisorctl update  > /dev/null 2>&1 || true
sudo supervisorctl restart "$PROGRAMA_SUPERVISOR"
sleep 3

# ── 4. Estado final ────────────────────────────────────
echo "[4/4] Estado del servicio:"
sudo supervisorctl status "$PROGRAMA_SUPERVISOR"

echo ""
echo "======================================================"
echo "   ACTUALIZACION COMPLETADA"
echo "======================================================"
echo ""
echo "Logs en tiempo real:"
echo "  sudo tail -f /var/log/migrador-bd.err.log"
echo "  sudo tail -f /var/log/migrador-bd.out.log"
echo ""
