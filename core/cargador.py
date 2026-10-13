import json
from typing import List
from core.modelos import FichaHuesped

class CargadorJornada:
    @staticmethod
    def cargar(ruta_json: str) -> List[FichaHuesped]:
        with open(ruta_json, "r", encoding="utf-8") as f:
            datos = json.load(f)
        procesos = []
        for p in datos.get("solicitudes", []):
            procesos.append(
                FichaHuesped(
                    pid=p["pid"],
                    llegada=p["llegada"],
                    duracion=p["duracion"],
                    prioridad=p["prioridad"],
                    huesped=p.get("huesped", ""),
                    tramite=p.get("tramite", "")
                )
            )
        return procesos
