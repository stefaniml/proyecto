# Inicializador de módulo 1 — Procesos, hilos y planificación
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
ESCENARIOS = RAIZ / "escenarios"
RESULTADOS = RAIZ / "resultados"


def ejecutar(parte="todo", jornada="jornada_corta", quantum=4):
    """Lo que llama main.py. parte: planificacion | hilos | graficos | todo."""
    from modulo1_procesos import graficos, planificacion
    from modulo1_procesos.procesos_hilos import hilos

    partes = {
        "hilos": ("HILOS · ¿una tarea tras otra, o todas a la vez?", hilos.ejecutar),
        "planificacion": ("PLANIFICACIÓN · ¿a quién atiende primero la recepción?",
                          lambda: planificacion.ejecutar(jornada, quantum)),
        "graficos": ("GRÁFICOS · figuras para el informe", graficos.ejecutar),
    }
    for nombre, (titulo, correr) in partes.items():
        if parte in ("todo", nombre):
            print(f"\n{'#' * 78}\n#  MÓDULO 1 · {titulo}\n{'#' * 78}\n")
            correr()
