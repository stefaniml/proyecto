from typing import List, Optional

class GestorContiguo:
    def __init__(self, capacidad_total: int = 12):
        self.capacidad = capacidad_total
        self.memoria: List[Optional[str]] = [None] * capacidad_total

    def asignar(self, proceso: str, tamano: int, estrategia: str = "Primer Ajuste") -> bool:
        bloques_libres = self._obtener_huecos()
        
        if estrategia == "Primer Ajuste":
            for inicio, longitud in bloques_libres:
                if longitud >= tamano:
                    self._marcar(inicio, tamano, proceso)
                    return True
        return False

    def _obtener_huecos(self):
        huecos = []
        inicio = None
        longitud = 0
        for i, slot in enumerate(self.memoria):
            if slot is None:
                if inicio is None:
                    inicio = i
                longitud += 1
            else:
                if inicio is not None:
                    huecos.append((inicio, longitud))
                    inicio = None
                    longitud = 0
        if inicio is not None:
            huecos.append((inicio, longitud))
        return huecos

    def _marcar(self, inicio: int, tamano: int, proceso: str):
        for i in range(inicio, inicio + tamano):
            self.memoria[i] = proceso

    def obtener_fragmentacion_externa(self, tamano_solicitado: int) -> int:
        huecos = self._obtener_huecos()
        total_libre = sum(l for _, l in huecos)
        max_continuo = max((l for _, l in huecos), default=0)
        if total_libre >= tamano_solicitado and max_continuo < tamano_solicitado:
            return total_libre
        return 0
