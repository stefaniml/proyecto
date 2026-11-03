"""Pruebas del Módulo 2 · Sincronización (semana 5).

Para qué sirven: el taller pide demostrar tres cosas, y cada prueba demuestra
una. No comprueban que el programa "no se caiga": comprueban que se cumple lo
que dice la teoría.

  1. Sin exclusión mutua, la misma habitación se entrega más de una vez.
  2. Con el mutex se entrega exactamente una.
  3. El armario no pierde ni duplica sábanas y nunca pasa de su capacidad.
  4. Con asignación asimétrica no hay interbloqueo en 20 rondas seguidas.

Un detalle importante: "sin mutex" se comprueba con "más de una vez" y no con
un número fijo, porque cuántas veces se pisan depende del instante exacto en
que se crucen los hilos. Lo que la teoría garantiza es que puede pasar, no
cuántas veces pasa.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from modulo2_sincronizacion.interbloqueo import PasilloDeLlaves
from modulo2_sincronizacion.limpieza import BufferLimpieza
from modulo2_sincronizacion.registro import RegistroHotel

RECEPCIONISTAS = 5
SABANAS = 10
CAPACIDAD = 3
HUESPEDES = 5
RONDAS = 20          # el taller pide repetir al menos 20 veces


# ===================================== 1. condición de carrera y mutex ===
def test_sin_mutex_la_habitacion_se_entrega_mas_de_una_vez():
    r = RegistroHotel(usar_mutex=False).simular(RECEPCIONISTAS)
    assert r["escrituras"] > 1, "sin candado deberían pisarse entre ellos"
    assert r["sobreventas"] >= 1


def test_con_mutex_se_entrega_exactamente_una_vez():
    r = RegistroHotel(usar_mutex=True).simular(RECEPCIONISTAS)
    assert r["escrituras"] == 1
    assert r["sobreventas"] == 0


# ========================================= 2. productor-consumidor =======
def test_el_armario_no_pierde_ni_duplica_sabanas():
    a = BufferLimpieza(capacidad=CAPACIDAD).simular(total=SABANAS)
    assert a["producidos"] == a["consumidos"] == SABANAS
    assert a["sin_perdidas"]
    assert a["armario_vacio"]


def test_el_armario_nunca_pasa_de_su_capacidad():
    """Es lo que demuestra que el semáforo 'vacios' está haciendo su trabajo."""
    a = BufferLimpieza(capacidad=CAPACIDAD).simular(total=SABANAS)
    assert a["ocupacion_maxima"] <= CAPACIDAD


# =============================================== 3. interbloqueo =========
def test_sin_orden_alguien_se_queda_esperando():
    """Todos toman la llave de su izquierda: el círculo se cierra."""
    d = PasilloDeLlaves(huespedes=HUESPEDES).simular(con_orden=False)
    assert d["bloqueados"] >= 1
    assert d["hubo_interbloqueo"]


def test_con_asignacion_asimetrica_nunca_hay_interbloqueo():
    """Taller, punto 4: 20 rondas seguidas y en todas terminan los cinco."""
    for ronda in range(RONDAS):
        d = PasilloDeLlaves(huespedes=HUESPEDES).simular(con_orden=True)
        assert d["entraron"] == HUESPEDES, f"se trabó en la ronda {ronda + 1}"
        assert d["bloqueados"] == 0
