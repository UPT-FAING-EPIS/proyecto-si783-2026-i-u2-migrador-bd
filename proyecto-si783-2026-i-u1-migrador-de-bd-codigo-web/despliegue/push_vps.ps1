# =====================================================
#  push_vps.ps1  —  Subir cambios y reiniciar en VPS
#  Uso: .\despliegue\push_vps.ps1
#       .\despliegue\push_vps.ps1 -Mensaje "mi commit" -Usuario root
# =====================================================
param(
    [string]$Mensaje  = "deploy: actualizacion automatica $(Get-Date -Format 'yyyy-MM-dd HH:mm')",
    [string]$VPS      = "207.180.218.158",
    [string]$Usuario  = "root",           # <-- cambia si usas otro usuario SSH
    [string]$Puerto   = "22",
    [string]$Directorio = "/opt/migrador-bd"
)

$ErrorActionPreference = "Stop"

Write-Host ""
Write-Host "======================================================" -ForegroundColor Cyan
Write-Host "   DESPLIEGUE MigradorBD  →  VPS $VPS" -ForegroundColor Cyan
Write-Host "======================================================" -ForegroundColor Cyan
Write-Host ""

# ── 1. Git add + commit + push ─────────────────────
Write-Host "[1/4] Preparando cambios locales..." -ForegroundColor Yellow

git add -A
$statusOutput = git status --porcelain
if ($statusOutput) {
    Write-Host "      Commiteando: $Mensaje" -ForegroundColor Gray
    git commit -m $Mensaje
} else {
    Write-Host "      Sin cambios nuevos, solo se hara push." -ForegroundColor Gray
}

Write-Host "[2/4] Subiendo a GitHub..." -ForegroundColor Yellow
git push
Write-Host "      Push completado." -ForegroundColor Green

# ── 2. SSH al VPS: pull + reiniciar supervisor ─────
Write-Host "[3/4] Conectando al VPS ($Usuario@$VPS)..." -ForegroundColor Yellow

$comandoRemoto = @"
set -e
echo '--- Git pull ---'
cd $Directorio
git pull origin main 2>&1 || git pull origin master 2>&1

echo '--- Instalando dependencias (si cambiaron) ---'
source $Directorio/venv/bin/activate 2>/dev/null || true
pip install -q -r $Directorio/requirements_web.txt 2>/dev/null || true

echo '--- Reiniciando Supervisor ---'
sudo supervisorctl reread
sudo supervisorctl update
sudo supervisorctl restart migrador-bd

echo '--- Estado del servicio ---'
sudo supervisorctl status migrador-bd
"@

ssh -p $Puerto "${Usuario}@${VPS}" $comandoRemoto

# ── 3. Resultado ───────────────────────────────────
Write-Host ""
Write-Host "[4/4] Verificando estado remoto..." -ForegroundColor Yellow
ssh -p $Puerto "${Usuario}@${VPS}" "sudo supervisorctl status migrador-bd"

Write-Host ""
Write-Host "======================================================" -ForegroundColor Green
Write-Host "   DESPLIEGUE COMPLETADO" -ForegroundColor Green
Write-Host "   URL: http://$VPS" -ForegroundColor Green
Write-Host "======================================================" -ForegroundColor Green
Write-Host ""
Write-Host "Comandos utiles en el VPS:" -ForegroundColor Cyan
Write-Host "  Ver logs:      ssh ${Usuario}@${VPS} 'tail -f /var/log/migrador-bd.err.log'" -ForegroundColor Gray
Write-Host "  Solo restart:  ssh ${Usuario}@${VPS} 'sudo supervisorctl restart migrador-bd'" -ForegroundColor Gray
Write-Host "  Estado:        ssh ${Usuario}@${VPS} 'sudo supervisorctl status migrador-bd'" -ForegroundColor Gray
Write-Host ""
