from enum import Enum
from dataclasses import dataclass, field
from typing import List, Optional

class EstadoProceso(Enum):
    NUEVO = "Nuevo"
    LISTO = "Listo"
    EJECUCION = "En Ejecución"
    BLOQUEADO = "Bloqueado"
    TERMINADO = "Terminado"

@dataclass
class FichaHuesped:  # Equivalente a Process Control Block (PCB)
    pid: str
    llegada: int
    duracion: int
    prioridad: int
    duracion_restante: int = 0
    estado: EstadoProceso = EstadoProceso.NUEVO
    tiempo_inicio: Optional[int] = None
    tiempo_fin: Optional[int] = None
    tiempo_espera: int = 0
    
    def __post_init__(self):
        self.duracion_restante = self.duracion

@dataclass
class EventoBitacora:
    tiempo: int
    pid: str
    descripcion: str
    estado_anterior: Optional[EstadoProceso] = None
    estado_nuevo: Optional[EstadoProceso] = None
