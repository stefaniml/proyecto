"""Pruebas del Módulo 1.  python -m pytest tests -q

La jornada corta (5 solicitudes) es pequeña a propósito: sus promedios se
calcularon a mano y el simulador debe reproducirlos exactamente.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest

from core.cargador import CargadorJornada
from modulo1_procesos import ESCENARIOS
from modulo1_procesos.planificacion import correr

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
