from enum import Enum
from dataclasses import dataclass
from typing import Optional

class EstadoProceso(Enum):
    NUEVO = "Nuevo"
    LISTO = "Listo"
    EJECUCION = "En Ejecución"
    BLOQUEADO = "Bloqueado"
    TERMINADO = "Terminado"

@dataclass
class FichaHuesped:
    pid: str
    llegada: int
    duracion: int
    prioridad: int
    duracion_restante: int = 0
    estado: EstadoProceso = EstadoProceso.NUEVO
    tiempo_inicio: Optional[int] = None
    tiempo_fin: Optional[int] = None
    tiempo_espera: int = 0
    huesped: str = ""
    tramite: str = ""

    def __post_init__(self):
        self.duracion_restante = self.duracion

@dataclass
class EventoBitacora:
    tiempo: int
    modulo: str
    descripcion: str
