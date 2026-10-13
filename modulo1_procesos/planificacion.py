"""Módulo 1 · Semana 4 — Planificación: FCFS, SJF, Round Robin y Prioridad.

El mostrador de recepción es la CPU y cada solicitud de un huésped es un
proceso. Las cuatro políticas usan el mismo motor (planificar); solo cambia
el criterio con el que se elige al siguiente huésped del lobby.
"""
import json
from copy import deepcopy

from core.bitacora import Bitacora
from core.cargador import CargadorJornada
from core.metricas import CalculadorMetricas
from core.modelos import EstadoProceso
from core.reloj import RelojLogico
from modulo1_procesos import ESCENARIOS, RESULTADOS


# --------------------------------------------- criterio de cada política ---
def fcfs(cola):
    """Primero en llegar, primero en ser atendido."""
    return min(cola, key=lambda f: (f.llegada, f.pid))


def sjf(cola):
    """Entre los que esperan, el trámite más corto."""
    return min(cola, key=lambda f: (f.duracion, f.llegada, f.pid))


def round_robin(cola):
    """El primero de la fila; si no termina en su quantum, vuelve al final."""
    return cola[0]


def prioridad(cola):
    """El de mayor prioridad (1 = la más alta)."""
    return min(cola, key=lambda f: (f.prioridad, f.llegada, f.pid))


POLITICAS = {"FCFS": fcfs, "SJF": sjf, "Round Robin": round_robin, "Prioridad": prioridad}


# ----------------------------------------------------------------- motor ---
def planificar(fichas, elegir, quantum=None, nombre=""):
    """Atiende la jornada en un solo mostrador.

    quantum=None -> no expropiativo: cada huésped se atiende hasta terminar.
    quantum=n    -> expropiativo: n minutos y vuelve al final de la cola.
    Devuelve las fichas terminadas, el diagrama de Gantt y la bitácora.
    """
    pendientes = sorted(deepcopy(fichas), key=lambda f: (f.llegada, f.pid))
    cola, terminadas, gantt = [], [], []
    reloj, bitacora = RelojLogico(), Bitacora()

    def admitir():                       # pasan al lobby los que ya llegaron
        while pendientes and pendientes[0].llegada <= reloj.obtener():
            ficha = pendientes.pop(0)
            ficha.estado = EstadoProceso.LISTO
            cola.append(ficha)

    admitir()
    while cola or pendientes:
        if not cola:                     # mostrador ocioso: salta al siguiente arribo
            reloj.avanzar(pendientes[0].llegada - reloj.obtener())
            admitir()
            continue

        f = elegir(cola)
        cola.remove(f)
        f.estado = EstadoProceso.EJECUCION
        t = reloj.obtener()
        if f.tiempo_inicio is None:
            f.tiempo_inicio = t
        bitacora.registrar(t, nombre, f"{f.pid} inicia")

        corre = f.duracion_restante if quantum is None else min(quantum, f.duracion_restante)
        gantt.append((f.pid, t, t + corre))
        reloj.avanzar(corre)
        f.duracion_restante -= corre
        admitir()                        # los que llegaron mientras atendía

        if f.duracion_restante:          # se acabó su quantum: vuelve a la cola
            f.estado = EstadoProceso.LISTO
            cola.append(f)
            bitacora.registrar(reloj.obtener(), nombre, f"{f.pid} pausa")
        else:
            f.estado = EstadoProceso.TERMINADO
            f.tiempo_fin = reloj.obtener()
            f.tiempo_espera = f.tiempo_fin - f.llegada - f.duracion
            terminadas.append(f)
            bitacora.registrar(f.tiempo_fin, nombre, f"{f.pid} termina")

    terminadas.sort(key=lambda f: (f.llegada, f.pid))
    return terminadas, gantt, bitacora


def verificar(bitacora, fichas):
    """Reconstruye inicio y fin leyendo SOLO la bitácora y los compara con
    las fichas. Si coinciden, la bitácora es fiel a lo que ocurrió."""
    inicio, fin = {}, {}
    for ev in bitacora.eventos:
        pid, accion = ev.descripcion.split()
        if accion == "inicia":
            inicio.setdefault(pid, ev.tiempo)
        elif accion == "termina":
            fin[pid] = ev.tiempo
    return all(inicio.get(f.pid) == f.tiempo_inicio and fin.get(f.pid) == f.tiempo_fin
               for f in fichas)


def correr(fichas, quantum=4):
    """Las cuatro políticas sobre la misma jornada."""
    resultados = {}
    for nombre, elegir in POLITICAS.items():
        q = quantum if elegir is round_robin else None
        terminadas, gantt, bitacora = planificar(fichas, elegir, q, nombre)
        resultados[nombre] = {
            "fichas": terminadas,
            "gantt": gantt,
            "bitacora": bitacora,
            "metricas": CalculadorMetricas.resumen_planificacion(terminadas),
            "verificado": verificar(bitacora, terminadas),
        }
    return resultados


# ---------------------------------------------------------------- salida ---
def imprimir(resultados, quantum):
    for nombre, r in resultados.items():
        print(f"\n{nombre}" + (f"  (quantum = {quantum} min)" if nombre == "Round Robin" else ""))
        print(f"  {'PID':<5}{'Huésped':<20}{'Lleg':>5}{'Dur':>5}{'Pri':>5}"
              f"{'Ini':>5}{'Fin':>5}{'Espera':>8}{'Resp':>6}{'Retorno':>9}")
        for f in r["fichas"]:
            print(f"  {f.pid:<5}{f.huesped[:19]:<20}{f.llegada:>5}{f.duracion:>5}{f.prioridad:>5}"
                  f"{f.tiempo_inicio:>5}{f.tiempo_fin:>5}{f.tiempo_espera:>8}"
                  f"{f.tiempo_inicio - f.llegada:>6}{f.tiempo_fin - f.llegada:>9}")
        print("  Gantt: " + "  ".join(f"{p}[{a}-{b}]" for p, a, b in r["gantt"]))

    print(f"\n{'COMPARACIÓN':<16}{'Espera':>10}{'Respuesta':>11}{'Retorno':>10}")
    for nombre, r in resultados.items():
        m = r["metricas"]
        print(f"{nombre:<16}{m['espera_promedio']:>10.2f}"
              f"{m['respuesta_promedio']:>11.2f}{m['retorno_promedio']:>10.2f}")
    print("\n  espera = fin - llegada - duración · respuesta = inicio - llegada"
          " · retorno = fin - llegada")


def ejecutar(jornada="jornada_corta", quantum=4):
    fichas = CargadorJornada.cargar(ESCENARIOS / f"{jornada}.json")
    print(f"  Jornada: {jornada} · {len(fichas)} solicitudes")
    resultados = correr(fichas, quantum)
    imprimir(resultados, quantum)

    RESULTADOS.mkdir(exist_ok=True)
    for nombre, r in resultados.items():
        r["bitacora"].guardar(RESULTADOS / f"m1_bitacora_{nombre.lower().replace(' ', '_')}.txt")
    with open(RESULTADOS / "m1_metricas.json", "w", encoding="utf-8") as f:
        json.dump({n: {"metricas": r["metricas"], "gantt": r["gantt"]}
                   for n, r in resultados.items()}, f, indent=2, ensure_ascii=False)

    ok = all(r["verificado"] for r in resultados.values())
    print(f"\n  Métricas recalculadas desde la bitácora: {'coinciden' if ok else 'NO COINCIDEN'}")
    print("  Bitácoras y métricas en resultados/m1_*")
    return resultados
