"""Gráficos de TODOS los módulos, con un mismo estilo.

Cada módulo deja sus datos en resultados/ y aquí se dibujan sus figuras.
Para añadir las de otro módulo: escribir su función (usando las
herramientas comunes de abajo) y registrarla en FIGURAS.

    Desde el menú de main.py, opción «Gráficos»: dibuja las que tengan datos.
"""
import json

import matplotlib
matplotlib.use("Agg")           # sin ventana: solo guarda el archivo
import matplotlib.pyplot as plt

from pathlib import Path

RESULTADOS = Path(__file__).resolve().parent.parent / "resultados"

GUINDA, ORO, TINTA, SUAVE, MALLA = "#7A1F2B", "#D9A441", "#2E2422", "#8C7F79", "#EDE7E7"


# ===================================================== herramientas comunes ===
def _leer(nombre):
    """Lee un JSON de resultados/; None si ese módulo aún no se ejecutó."""
    ruta = RESULTADOS / nombre
    if not ruta.exists():
        return None
    return json.loads(ruta.read_text(encoding="utf-8"))


def _guardar(fig, ax, nombre):
    ax.spines[["top", "right"]].set_visible(False)
    ax.tick_params(colors=SUAVE)
    ax.set_axisbelow(True)
    fig.tight_layout()
    salida = RESULTADOS / nombre
    fig.savefig(salida, dpi=200)
    plt.close(fig)
    return salida


def _barras_pareadas(nombres, a, b, etiqueta_a, etiqueta_b, unidad, archivo):
    """Dos barras por grupo: la forma común de las figuras de Semana 3 y 4."""
    x = range(len(nombres))
    fig, ax = plt.subplots(figsize=(8.6, 4.4))
    for desplaz, valores, etiqueta, color in [(-0.19, a, etiqueta_a, GUINDA),
                                              (0.19, b, etiqueta_b, ORO)]:
        barras = ax.bar([i + desplaz for i in x], valores, 0.38, label=etiqueta, color=color)
        ax.bar_label(barras, fmt="%.2f", fontsize=9, color=TINTA, padding=2)
    ax.set_xticks(list(x), nombres, color=TINTA)
    ax.set_ylabel(unidad, color=SUAVE)
    ax.set_ylim(0, max(a + b) * 1.2)
    ax.legend(frameon=False, fontsize=9)
    ax.grid(axis="y", color=MALLA)
    return _guardar(fig, ax, archivo)


# ================================================================ Módulo 1 ===
def comparacion_politicas():
    datos = _leer("m1_metricas.json")
    if not datos:
        return None
    return _barras_pareadas(
        list(datos),
        [d["metricas"]["espera_promedio"] for d in datos.values()],
        [d["metricas"]["respuesta_promedio"] for d in datos.values()],
        "Espera promedio", "Respuesta promedio", "minutos", "m1_politicas.png")


def hilos():
    filas = _leer("m1_hilos.json")
    if not filas:
        return None
    return _barras_pareadas(
        [f'{f["tramite"]} ({f["tareas"]} tareas)' for f in filas],
        [f["sin_hilos"] for f in filas],
        [f["con_hilos"] for f in filas],
        "Sin hilos", "Con hilos", "segundos", "m1_hilos.png")


def fork_exec():
    """Cuánto duró cada proceso, y la jornada con fork frente a uno tras otro."""
    filas = _leer("m1_traza_fork.json")
    if not filas:
        return None
    nombres = [f'{f["pid"]} · {f["huesped"]}' for f in filas]
    duraciones = [f["duracion_ms"] for f in filas]
    con_fork, sin_fork = max(duraciones), sum(duraciones)

    fig, ax = plt.subplots(figsize=(8.6, 0.5 * len(filas) + 2.4))
    ax.barh(nombres, duraciones, color=GUINDA)
    ax.barh(["", "Con fork (en paralelo)", "Sin fork (uno tras otro)"],
            [0, con_fork, sin_fork], color=[GUINDA, GUINDA, ORO])
    for i, v in enumerate(duraciones + [None, con_fork, sin_fork]):
        if v:
            ax.text(v + sin_fork * 0.01, i, f"{v:.0f} ms", va="center", fontsize=9, color=TINTA)
    ax.invert_yaxis()
    ax.set_xlabel("milisegundos", color=SUAVE)
    ax.set_xlim(0, sin_fork * 1.15)
    ax.grid(axis="x", color=MALLA)
    return _guardar(fig, ax, "m1_fork_exec.png")


# ================================================================ Módulo 2 ===
# (aquí van las figuras de sincronización)

# ================================================================ Módulo 3 ===
# (aquí van las figuras de memoria)


# (módulo, figura, función, qué ejecutar antes si faltan datos)
FIGURAS = [
    (1, "comparación de políticas", comparacion_politicas, "la opción Planificación del menú"),
    (1, "con y sin hilos", hilos, "la opción Hilos del menú"),
    (1, "fork y exec", fork_exec, "la opción de procesos en C del menú (Linux/WSL)"),
]


def ejecutar():
    for modulo, nombre, generar, falta in FIGURAS:
        salida = generar()
        if salida:
            print(f"  M{modulo} · {nombre:<26} -> resultados/{salida.name}")
        else:
            print(f"  M{modulo} · {nombre:<26} -- sin datos. Corre antes:  {falta}")
