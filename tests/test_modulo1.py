"""Pruebas del Módulo 1. Se ejecutan desde el menú (Pruebas automáticas) o con
python -m pytest tests -v

La jornada corta (5 solicitudes) es pequeña a propósito: sus promedios se
calcularon a mano y el simulador debe reproducirlos exactamente.
"""
import json
import os
import shutil
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest

from core.cargador import CargadorJornada
from modulo1_procesos import ESCENARIOS, RAIZ, RESULTADOS
from modulo1_procesos.hilos import hilos
from modulo1_procesos.planificacion.planificador import correr

# =============================================================== planificación ===

# (espera, respuesta, retorno) promedio de la jornada corta, calculados a mano
ESPERADO = {
    "FCFS":        (8.20, 8.20, 13.20),
    "SJF":         (5.80, 5.80, 10.80),
    "Round Robin": (10.60, 4.80, 15.60),
    "Prioridad":   (10.40, 10.40, 15.40),
}


@pytest.fixture(scope="module")
def resultados():
    return correr(CargadorJornada.cargar(ESCENARIOS / "jornada_corta.json"), quantum=4)


@pytest.mark.parametrize("politica", ESPERADO)
def test_reproduce_los_promedios_calculados_a_mano(resultados, politica):
    m = resultados[politica]["metricas"]
    obtenido = (m["espera_promedio"], m["respuesta_promedio"], m["retorno_promedio"])
    assert tuple(round(v, 2) for v in obtenido) == ESPERADO[politica]


def test_sjf_minimiza_la_espera(resultados):
    esperas = {n: r["metricas"]["espera_promedio"] for n, r in resultados.items()}
    assert esperas["SJF"] == min(esperas.values())


def test_round_robin_minimiza_la_respuesta(resultados):
    resp = {n: r["metricas"]["respuesta_promedio"] for n, r in resultados.items()}
    assert resp["Round Robin"] == min(resp.values())


def test_ninguna_politica_pierde_ni_duplica_solicitudes(resultados):
    for r in resultados.values():
        assert sorted(f.pid for f in r["fichas"]) == ["P1", "P2", "P3", "P4", "P5"]


def test_las_metricas_coinciden_con_la_bitacora(resultados):
    assert all(r["verificado"] for r in resultados.values())


def test_round_robin_parte_la_solicitud_larga(resultados):
    """Con quantum 4, la delegación de 9 minutos ocupa el mostrador tres veces (4 + 4 + 1)."""
    assert sum(1 for pid, _, _ in resultados["Round Robin"]["gantt"] if pid == "P3") == 3


def test_la_jornada_dia_tambien_se_verifica():
    fichas = CargadorJornada.cargar(ESCENARIOS / "jornada_dia.json")
    assert all(r["verificado"] for r in correr(fichas).values())


# ======================================================================= hilos ===
def test_con_hilos_las_tareas_van_a_la_vez():
    """3 tareas de 0.15 s: sin hilos ~0.45 s; con hilos dura lo que una sola."""
    assert hilos.sin_hilos(3) >= 3 * hilos.DURACION
    assert hilos.con_hilos(3) < 2 * hilos.DURACION


# ==================================================== procesos: fork, exec y wait ===
COMPILADOR = shutil.which("gcc") or shutil.which("clang")


@pytest.mark.skipif(os.name != "posix" or not COMPILADOR,
                    reason="fork() y exec() necesitan Linux/WSL con gcc o clang")
def test_fork_exec_atiende_a_todos_en_paralelo():
    carpeta = RAIZ / "modulo1_procesos" / "procesos_c"
    for nombre in ("hijo_atender", "padre_mostrador"):
        subprocess.run([COMPILADOR, "-O2", f"{nombre}.c", "-o", nombre], cwd=carpeta, check=True)
    subprocess.run([str(carpeta / "padre_mostrador")], cwd=RAIZ, check=True,
                   capture_output=True)

    traza = json.loads((RESULTADOS / "m1_traza_fork.json").read_text(encoding="utf-8"))
    duraciones = {p["pid"]: p["duracion_ms"] for p in traza}
    assert sorted(duraciones) == ["P1", "P2", "P3", "P4", "P5"]   # un hijo por solicitud
    assert len({p["pid_so"] for p in traza}) == 5                    # cada uno con su PID
    assert duraciones["P3"] >= 900          # el trámite de 9 min dura al menos 900 ms
    assert max(duraciones.values()) < 0.6 * sum(duraciones.values())  # en paralelo
