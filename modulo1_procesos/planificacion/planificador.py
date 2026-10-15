"""Módulo 1 · Semana 4 — Planificación de procesos.

El mostrador de recepción es la CPU y cada solicitud de un huésped es un
proceso (FichaHuesped = PCB). Este archivo tiene tres partes:

  1. planificar()  el motor que comparten las cuatro políticas
  2. verificar()   comprueba que la bitácora coincide con los resultados
  3. ejecutar()    corre las cuatro políticas, imprime y guarda

Cada política (fcfs.py, sjf.py, …) solo decide a quién atiende el mostrador
a continuación. Todo lo demás es igual para las cuatro.
"""
import json
from copy import deepcopy

from core.bitacora import Bitacora
from core.cargador import CargadorJornada
from core.metricas import CalculadorMetricas
from core.modelos import EstadoProceso
from core.reloj import RelojLogico
from modulo1_procesos import ESCENARIOS, RESULTADOS
from modulo1_procesos.planificacion import fcfs, prioridad, round_robin, sjf


# ============================================================ 1. el motor ===
def planificar(fichas, elegir, quantum=None, nombre=""):
    """Atiende una jornada completa en un único mostrador.

    elegir(cola) -> ficha : el criterio de la política.
    quantum=None          : no expropiativo, atiende hasta terminar.
    quantum=n             : expropiativo, atiende n minutos y devuelve a la cola.
    """
    pendientes = sorted(deepcopy(fichas), key=lambda f: (f.llegada, f.pid))
    cola, terminadas, gantt = [], [], []
    reloj = RelojLogico()
    bitacora = Bitacora()

    def admitir():
        """Pasa al lobby (cola de listos) a los que ya llegaron."""
        while pendientes and pendientes[0].llegada <= reloj.obtener():
            f = pendientes.pop(0)
            f.estado = EstadoProceso.LISTO
            cola.append(f)
            bitacora.registrar(f.llegada, nombre, f"{f.pid} entra_al_lobby")

    admitir()
    while cola or pendientes:
        if not cola:                            # mostrador ocioso: salta al siguiente arribo
            reloj.avanzar(pendientes[0].llegada - reloj.obtener())
            admitir()
            continue

        # ① LA POLÍTICA ELIGE a quién atender (FCFS, SJF, Prioridad o Round Robin)
        f = elegir(cola)
        cola.remove(f)
        f.estado = EstadoProceso.EJECUCION
        if f.tiempo_inicio is None:             # primera vez que llega al mostrador
            f.tiempo_inicio = reloj.obtener()
        bitacora.registrar(reloj.obtener(), nombre, f"{f.pid} ocupa_mostrador")

        # ② CUÁNTO TIEMPO lo atiende
        if quantum is None:
            atencion = f.duracion_restante                  # sin quantum: hasta terminar
        else:
            atencion = min(quantum, f.duracion_restante)    # Round Robin: como máximo el quantum

        # ③ PASA EL TIEMPO de la atención
        gantt.append((f.pid, reloj.obtener(), reloj.obtener() + atencion))
        reloj.avanzar(atencion)
        f.duracion_restante -= atencion

        admitir()                               # los que llegaron mientras era atendido

        # ④ ¿TERMINÓ? Sale del hotel. ¿No? Vuelve al final de la fila (Round Robin)
        if f.duracion_restante == 0:
            f.tiempo_fin = reloj.obtener()
            f.tiempo_espera = f.tiempo_fin - f.llegada - f.duracion
            f.estado = EstadoProceso.TERMINADO
            terminadas.append(f)
            bitacora.registrar(reloj.obtener(), nombre, f"{f.pid} termina")
        else:
            f.estado = EstadoProceso.LISTO
            cola.append(f)
            bitacora.registrar(reloj.obtener(), nombre, f"{f.pid} fin_de_quantum")

    terminadas.sort(key=lambda f: (f.llegada, f.pid))
    return terminadas, gantt, bitacora


# ===================================================== 2. la verificación ===
def verificar(bitacora, fichas):
    """Reconstruye inicio y fin de cada solicitud leyendo SOLO la bitácora y
    los compara con las fichas. Si coinciden, la bitácora es fiel."""
    inicio, fin = {}, {}
    for evento in bitacora.eventos:
        pid, accion = evento.descripcion.split()
        if accion == "ocupa_mostrador" and pid not in inicio:
            inicio[pid] = evento.tiempo
        if accion == "termina":
            fin[pid] = evento.tiempo
    return all(inicio.get(f.pid) == f.tiempo_inicio and fin.get(f.pid) == f.tiempo_fin
               for f in fichas)


# ================================================== 3. correr y comparar ===
def correr(fichas, quantum=4):
    """Ejecuta las cuatro políticas sobre la misma jornada."""
    politicas = [                               # (nombre, criterio, quantum)
        ("FCFS",        fcfs.elegir,        None),
        ("SJF",         sjf.elegir,         None),
        ("Round Robin", round_robin.elegir, quantum),   # la única que usa quantum
        ("Prioridad",   prioridad.elegir,   None),
    ]
    resultados = {}
    for nombre, elegir, q in politicas:
        terminadas, gantt, bitacora = planificar(fichas, elegir, q, nombre)
        resultados[nombre] = {
            "fichas": terminadas,
            "gantt": gantt,
            "bitacora": bitacora,
            "metricas": CalculadorMetricas.resumen_planificacion(terminadas),
            "verificado": verificar(bitacora, terminadas),
        }
    return resultados


def imprimir(resultados, quantum):
    for nombre, r in resultados.items():
        print(f"\n{nombre}" + (f"  (quantum = {quantum} min)" if nombre == "Round Robin" else ""))
        print(f"  {'PID':<5}{'Huésped':<20}{'Lleg':>5}{'Dur':>5}{'Pri':>5}"
              f"{'Ini':>5}{'Fin':>5}{'Espera':>8}{'Resp':>6}{'Retorno':>9}")
        for f in r["fichas"]:
            print(f"  {f.pid:<5}{f.huesped[:19]:<20}{f.llegada:>5}{f.duracion:>5}{f.prioridad:>5}"
                  f"{f.tiempo_inicio:>5}{f.tiempo_fin:>5}{f.tiempo_espera:>8}"
                  f"{f.tiempo_inicio - f.llegada:>6}{f.tiempo_fin - f.llegada:>9}")
        print("  Orden de atención: " + "  ".join(f"{p}[{a}-{b}]" for p, a, b in r["gantt"]))

    print(f"\n{'COMPARACIÓN':<16}{'Espera':>10}{'Respuesta':>11}{'Retorno':>10}")
    for nombre, r in resultados.items():
        m = r["metricas"]
        print(f"{nombre:<16}{m['espera_promedio']:>10.2f}"
              f"{m['respuesta_promedio']:>11.2f}{m['retorno_promedio']:>10.2f}")
    print("\n  Espera    = fin - llegada - duración   (minutos en el lobby)")
    print("  Respuesta = inicio - llegada           (cuánto tarda en ser atendido)")
    print("  Retorno   = fin - llegada              (trámite de punta a punta)")


def guardar(resultados):
    """Una bitácora por política y un JSON con las métricas."""
    RESULTADOS.mkdir(exist_ok=True)
    for nombre, r in resultados.items():
        r["bitacora"].guardar(RESULTADOS / f"m1_bitacora_{nombre.lower().replace(' ', '_')}.txt")
    with open(RESULTADOS / "m1_metricas.json", "w", encoding="utf-8") as f:
        json.dump({n: {"metricas": r["metricas"], "gantt": r["gantt"]}
                   for n, r in resultados.items()}, f, indent=2, ensure_ascii=False)


def ejecutar(jornada="jornada_corta", quantum=4):
    fichas = CargadorJornada.cargar(ESCENARIOS / f"{jornada}.json")
    print(f"  Jornada: {jornada} · {len(fichas)} solicitudes")
    resultados = correr(fichas, quantum)
    imprimir(resultados, quantum)
    guardar(resultados)

    ok = all(r["verificado"] for r in resultados.values())
    print(f"\n  Métricas recalculadas desde la bitácora: {'coinciden' if ok else 'NO COINCIDEN'}")
    print("  Bitácoras y métricas en resultados/m1_*")
    return resultados
