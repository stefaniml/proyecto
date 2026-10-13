from typing import List
from nucleo.modelos import FichaHuesped

class CalculadorMetricas:
    @staticmethod
    def resumen_planificacion(procesos: List[FichaHuesped]) -> dict:
        n = len(procesos)
        if n == 0:
            return {}
        total_espera = sum(p.tiempo_espera for p in procesos)
        total_retorno = sum((p.tiempo_fin - p.llegada) for p in procesos if p.tiempo_fin)
        return {
            "espera_promedio": total_espera / n,
            "retorno_promedio": total_retorno / n
        }
