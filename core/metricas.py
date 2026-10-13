from typing import List
from core.modelos import FichaHuesped

class CalculadorMetricas:
    @staticmethod
    def resumen_planificacion(procesos: List[FichaHuesped]) -> dict:
        n = len(procesos)
        if n == 0:
            return {}
        total_espera = sum(p.tiempo_espera for p in procesos)
        total_retorno = sum((p.tiempo_fin - p.llegada) for p in procesos if p.tiempo_fin)
        total_respuesta = sum((p.tiempo_inicio - p.llegada) for p in procesos if p.tiempo_inicio is not None)
        return {
            "espera_promedio": total_espera / n,
            "respuesta_promedio": total_respuesta / n,
            "retorno_promedio": total_retorno / n
        }
