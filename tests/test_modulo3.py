"""Pruebas del Módulo 3 · Memoria (semanas 6 y 7).

Para qué sirven: el taller de la semana 6 pide calcular a mano la dirección
física de tres direcciones virtuales y "verificarlas con su simulación". Eso
es literalmente lo que hacen estas pruebas: los valores esperados están
calculados a mano y escritos aquí, y la prueba exige que el simulador los
reproduzca.

  1. La MMU traduce las tres direcciones del ejemplo de clase.
  2. Pedir una página que no está en la tabla es un fallo de página.
  3. Con asignación contigua un grupo puede no entrar aunque sobre sitio.
  4. FIFO, LRU y Óptimo dan los fallos contados a mano sobre la misma secuencia.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest

from modulo3_memoria.contigua.asignador import GestorContiguo
from modulo3_memoria.paginacion.mmu import MMU
from modulo3_memoria.paginacion.reemplazo import AlgoritmosReemplazo

TAMANO_PAGINA = 4096
TABLA = {0: 5, 1: 2, 2: 7, 3: 0}     # tabla de páginas del ejemplo de clase

# (dirección virtual, página, desplazamiento, marco, dirección física a mano)
TRADUCCIONES = [
    (10_000, 2, 1_808, 7, 30_480),   # 7 x 4096 + 1808
    ( 5_000, 1,   904, 2,  9_096),   # 2 x 4096 +  904
    (     0, 0,     0, 5, 20_480),   # 5 x 4096 +    0
]

SECUENCIA = [7, 0, 1, 2, 0, 3, 0, 4, 2, 3, 0, 3, 2]
MARCOS = 3
FALLOS_A_MANO = {"fifo": 10, "lru": 9, "optimo": 7}


# ======================================== 1. traducción de direcciones ===
@pytest.mark.parametrize("virtual, pagina, desplazamiento, marco, fisica", TRADUCCIONES)
def test_la_direccion_fisica_coincide_con_el_calculo_a_mano(
        virtual, pagina, desplazamiento, marco, fisica):
    assert virtual // TAMANO_PAGINA == pagina            # la división da la página
    assert virtual % TAMANO_PAGINA == desplazamiento     # el resto, el desplazamiento
    assert TABLA[pagina] == marco                        # la tabla dice el marco
    assert MMU(TAMANO_PAGINA).traducir(virtual, TABLA) == fisica


def test_una_pagina_fuera_de_la_tabla_es_un_fallo_de_pagina():
    with pytest.raises(MemoryError):
        MMU(TAMANO_PAGINA).traducir(40_000, TABLA)       # página 9: no está cargada


# =========================================== 2. asignación contigua ======
def test_sobra_sitio_pero_el_grupo_de_tres_no_entra():
    """Fragmentación externa: 6 habitaciones libres, ninguna fila de 3 seguidas."""
    pasillo = GestorContiguo(capacidad_total=12)
    pasillo.memoria = ["A", None, "B", "B", None, "C", None, None, "D", None, "E", None]

    assert pasillo.memoria.count(None) == 6              # sitio de sobra
    assert pasillo.asignar("Grupo", 3) is False          # y aun así se le rechaza
    assert pasillo.obtener_fragmentacion_externa(3) == 6


# ======================================== 3. reemplazo de páginas ========
@pytest.mark.parametrize("algoritmo, esperado", sorted(FALLOS_A_MANO.items()))
def test_los_fallos_coinciden_con_el_conteo_a_mano(algoritmo, esperado):
    assert getattr(AlgoritmosReemplazo, algoritmo)(SECUENCIA, MARCOS) == esperado


def test_optimo_nunca_falla_mas_que_lru_ni_lru_mas_que_fifo():
    """Con la misma secuencia y los mismos marcos: Óptimo <= LRU <= FIFO."""
    f = {n: getattr(AlgoritmosReemplazo, n)(SECUENCIA, MARCOS) for n in FALLOS_A_MANO}
    assert f["optimo"] <= f["lru"] <= f["fifo"]
