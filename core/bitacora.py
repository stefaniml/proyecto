from typing import List
from core.modelos import EventoBitacora

class Bitacora:
    def __init__(self):
        self.eventos: List[EventoBitacora] = []

    def registrar(self, tiempo: int, modulo: str, descripcion: str):
        self.eventos.append(EventoBitacora(tiempo, modulo, descripcion))

    def guardar(self, ruta: str):
        with open(ruta, "w", encoding="utf-8") as f:
            for ev in self.eventos:
                f.write(f"[{ev.tiempo:04d}] [{ev.modulo}] {ev.descripcion}\n")
