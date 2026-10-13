"""Módulo 1 · Semana 3 — Hilos: uno o varios recepcionistas.

Un trámite tiene varias tareas (escenarios/tareas.json). Con un recepcionista
salen una tras otra; con un hilo por tarea, salen a la vez. Este archivo
cronometra las dos formas y guarda los tiempos en resultados/m1_hilos.csv.
"""
import csv
import json
import statistics
import threading
import time

from modulo1_procesos import ESCENARIOS, RESULTADOS

DURACION = 0.15        # segundos que "cuesta" cada tarea (espera de banco, impresora...)
REPETICIONES = 5       # se mide varias veces y se toma la mediana


def tarea():
    time.sleep(DURACION)


def sin_hilos(n):
    """Un recepcionista hace las n tareas, una después de otra."""
    inicio = time.perf_counter()
    for _ in range(n):
        tarea()
    return time.perf_counter() - inicio


def con_hilos(n):
    """Un hilo por tarea: todas avanzan a la vez."""
    inicio = time.perf_counter()
    hilos = [threading.Thread(target=tarea) for _ in range(n)]
    for h in hilos:
        h.start()
    for h in hilos:
        h.join()           # el trámite no se cierra hasta que todas acaban
    return time.perf_counter() - inicio


def ejecutar():
    print(f"  Cada tarea cuesta {DURACION} s · mediana de {REPETICIONES} mediciones\n")
    print(f"  {'Trámite':<10}{'Tareas':>7}{'Sin hilos':>12}{'Con hilos':>12}{'Mejora':>9}")

    filas = []
    tramites = json.loads((ESCENARIOS / "tareas.json").read_text(encoding="utf-8"))
    for tramite, tareas in tramites.items():
        n = len(tareas)
        sec = statistics.median(sin_hilos(n) for _ in range(REPETICIONES))
        con = statistics.median(con_hilos(n) for _ in range(REPETICIONES))
        filas.append({"tramite": tramite, "tareas": n, "sin_hilos": round(sec, 4),
                      "con_hilos": round(con, 4), "mejora": round(sec / con, 2)})
        print(f"  {tramite:<10}{n:>7}{sec:>11.2f}s{con:>11.2f}s{sec / con:>8.2f}×")

    print("\n  Sin hilos el tiempo crece con cada tarea; con hilos dura lo que la")
    print("  más lenta. No llega al ideal porque crear y esperar hilos también cuesta.")

    RESULTADOS.mkdir(exist_ok=True)
    ruta = RESULTADOS / "m1_hilos.csv"
    with open(ruta, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=filas[0])
        w.writeheader()
        w.writerows(filas)
    print(f"\n  Tiempos en resultados/{ruta.name}")
    return filas
