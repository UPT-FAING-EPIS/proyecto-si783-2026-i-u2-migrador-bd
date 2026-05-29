from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional
from datetime import datetime

@dataclass
class ConfiguracionConexion:
    motor: str
    host: str = "localhost"
    puerto: str = ""
    usuario: str = ""
    contrasena: str = ""
    nombre_bd: str = ""
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "motor": self.motor,
            "host": self.host,
            "puerto": self.puerto,
            "usuario": self.usuario,
            "contrasena": self.contrasena,
            "nombre_bd": self.nombre_bd
        }

@dataclass
class EsquemaTabla:
    nombre: str
    columnas: List[Dict[str, Any]]
    claves_primarias: List[str]
    claves_foraneas: List[Dict[str, Any]]
    indices: List[Dict[str, Any]]

@dataclass
class EstadoMigracion:
    proceso_id: str
    origen: Optional[ConfiguracionConexion] = None
    destino: Optional[ConfiguracionConexion] = None
    esquema: Optional[Dict[str, Any]] = None
    tablas_migrar: List[str] = field(default_factory=list)
    tablas_completadas: List[str] = field(default_factory=list)
    metricas: Dict[str, int] = field(default_factory=lambda: {
        "extraidos": 0,
        "cargados": 0,
        "errores": 0,
        "tablas_ok": 0
    })
    activo: bool = False
    pausado: bool = False
    fecha_inicio: Optional[datetime] = None
    fecha_fin: Optional[datetime] = None
    
    def progreso(self) -> float:
        if not self.tablas_migrar:
            return 0
        return (len(self.tablas_completadas) / len(self.tablas_migrar)) * 100
    
    def resumen(self) -> Dict[str, Any]:
        return {
            "origen": self.origen.to_dict() if self.origen else {},
            "destino": self.destino.to_dict() if self.destino else {},
            "tablas_totales": len(self.tablas_migrar),
            "tablas_completadas": len(self.tablas_completadas),
            "progreso": self.progreso(),
            "metricas": self.metricas,
            "fecha_inicio": self.fecha_inicio.isoformat() if self.fecha_inicio else None,
            "fecha_fin": self.fecha_fin.isoformat() if self.fecha_fin else None,
            "activo": self.activo
        }

@dataclass
class ReporteMigracion:
    estados: List[EstadoMigracion] = field(default_factory=list)
    
    def agregar_estado(self, estado: EstadoMigracion):
        self.estados.append(estado)
    
    def ultimo_estado(self) -> Optional[EstadoMigracion]:
        return self.estados[-1] if self.estados else None