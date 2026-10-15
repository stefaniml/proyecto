#!/usr/bin/env python3
"""SO-Sim · Hotel Las Estrellas — menú principal del simulador.

    python main.py          (Windows)
    python3 main.py         (Linux / WSL)

Muestra un menú numerado; cada opción ejecuta un módulo y al terminar vuelve
al menú. Las opciones en C (fork, exec, wait) solo aparecen en Linux, donde
se compilan solas con gcc o clang la primera vez.

Para añadir un módulo: escribir su función y agregar una línea en OPCIONES
(o en la lista de su submenú, como MODULO1).
"""
import os
import shutil
import subprocess
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent
sys.path.insert(0, str(RAIZ))

HAY_C = os.name == "posix"          # Linux / WSL: fork() y exec() existen
CARPETA_C = RAIZ / "modulo1_procesos" / "procesos_c"


# ================================================================ utilidades ===
def preguntar(texto, defecto):
    """Pide un valor; con Enter se queda el valor por defecto."""
    respuesta = input(f"  {texto} [{defecto}]: ").strip()
    return respuesta or defecto


def compilar(*programas):
    """Compila los .c que falten o hayan cambiado. Devuelve False si no se pudo."""
    compilador = shutil.which("gcc") or shutil.which("clang")
    if not compilador:
        print("  No se encontró gcc ni clang. Instálalo con:  sudo apt install build-essential")
        return False
    for nombre in programas:
        fuente, binario = CARPETA_C / f"{nombre}.c", CARPETA_C / nombre
        if binario.exists() and binario.stat().st_mtime >= fuente.stat().st_mtime:
            continue                                # ya está compilado y al día
        print(f"  Compilando {fuente.name} con {Path(compilador).name}...")
        r = subprocess.run([compilador, "-Wall", "-Wextra", "-O2", str(fuente), "-o", str(binario)],
                           capture_output=True, text=True)
        if r.returncode != 0:
            print(r.stderr)
            return False
    return True


# ================================================================== Módulo 1 ===
def m1_hilos():
    from modulo1_procesos.hilos import hilos
    hilos.ejecutar()


def m1_planificacion():
    from modulo1_procesos.planificacion import planificador
    quantum = preguntar("Quantum de Round Robin (minutos)", "4")
    if not quantum.isdigit() or int(quantum) < 1:
        print("  El quantum debe ser un entero positivo, se usa 4.")
        quantum = "4"
    print()
    planificador.ejecutar("jornada_corta", int(quantum))


def m1_fork_exec():
    """Programa en C: el SO crea procesos reales con fork(), exec() y wait()."""
    if not compilar("hijo_atender", "padre_mostrador"):
        return
    sys.stdout.flush()
    subprocess.run([str(CARPETA_C / "padre_mostrador")], cwd=RAIZ)   # usa la jornada corta


# ================================================================== Módulo 2 ===
def m2_sincronizacion():
    """Tres situaciones de la semana 5: carrera, productor-consumidor e interbloqueo."""
    from modulo2_sincronizacion.interbloqueo import PasilloDeLlaves
    from modulo2_sincronizacion.limpieza import BufferLimpieza
    from modulo2_sincronizacion.registro import RegistroHotel

    # --- 1. condición de carrera y exclusión mutua ---------------------------
    print("  [1] Condición de carrera · 5 recepcionistas reservan la 302 a la vez")
    for usar_mutex in (False, True):
        r = RegistroHotel(usar_mutex).simular(5)
        print(f"      {'Con mutex' if usar_mutex else 'Sin mutex'}   "
              f"{r['escrituras']} escritura(s)  ->  {r['sobreventas']} sobreventa(s)")

    # --- 2. productor-consumidor con semáforos -------------------------------
    a = BufferLimpieza(capacidad=3).simular(total=10)
    print(f"\n  [2] Productor-consumidor · armario de {a['capacidad']} sitios, "
          f"{a['producidos']} sábanas")
    print(f"      Producidas {a['producidos']} · recogidas {a['consumidos']} · "
          f"{'ninguna perdida' if a['sin_perdidas'] else 'HUBO PÉRDIDAS'}")
    print(f"      Ocupación máxima {a['ocupacion_maxima']} de {a['capacidad']}")
    print(f"      Esperas: lavandería {a['esperas_lavanderia']} (lleno) · "
          f"recepción {a['esperas_recepcion']} (vacío)")

    # --- 3. interbloqueo y cómo se previene ----------------------------------
    print("\n  [3] Interbloqueo · 5 huéspedes en círculo, cada uno necesita 2 llaves")
    for con_orden, como in ((False, "Todos: izquierda y luego derecha"),
                            (True, "El último empieza por la derecha")):
        d = PasilloDeLlaves(huespedes=5).simular(con_orden)
        print(f"      {como:<34}entraron {d['entraron']} de {d['huespedes']}  ->  "
              f"{d['bloqueados']} bloqueado(s)")


# ================================================================== Módulo 3 ===
def m3_memoria():
    from modulo3_memoria.contigua.asignador import GestorContiguo
    from modulo3_memoria.paginacion.mmu import MMU
    from modulo3_memoria.paginacion.reemplazo import AlgoritmosReemplazo

    pasillo = GestorContiguo(capacidad_total=12)
    for grupo, tamano in [("G1", 4), ("G2", 3), ("G3", 6)]:
        ok = pasillo.asignar(grupo, tamano)
        print(f"  Asignación contigua: {grupo} pide {tamano} habitaciones -> "
              f"{'asignado' if ok else 'rechazado'}")
    print("  Pasillo: " + " ".join(h or "--" for h in pasillo.memoria))

    mmu = MMU(tamano_pagina=4096)
    print(f"\n  MMU: dirección virtual 5000 con tabla {{0: 2, 1: 5}} -> física "
          f"{mmu.traducir(5000, {0: 2, 1: 5})}")

    secuencia, marcos = [7, 0, 1, 2, 0, 3, 0, 4, 2, 3, 0, 3, 2], 3
    print(f"\n  Reemplazo de páginas con {marcos} marcos, secuencia {secuencia}:")
    for nombre in ("fifo", "lru", "optimo"):
        fallos = getattr(AlgoritmosReemplazo, nombre)(secuencia, marcos)
        print(f"    {nombre.upper():<7} {fallos} fallos de página")


# ================================================================= gráficos ===
def graficos():
    from analisis import graficos as g
    g.ejecutar()


# ================================================================== pruebas ===
def pruebas():
    try:
        import pytest
    except ImportError:
        print("  Falta pytest. Instálalo con:  pip install -r requirements.txt")
        return
    pytest.main([str(RAIZ / "tests"), "-v", "-p", "no:cacheprovider"])


# ===================================================================== menú ===
# Cada opción es (texto, acción, ¿necesita C/Linux?). La acción es una función,
# o una lista de opciones: en ese caso se abre como submenú.
MODULO1 = [
    ("Procesos en C: fork, exec y wait (Linux/WSL)", m1_fork_exec, True),
    ("Hilos: el mismo trámite con y sin hilos", m1_hilos, False),
    ("Planificación: FCFS, SJF, Round Robin, Prioridad", m1_planificacion, False),
]

OPCIONES = [
    ("Módulo 1 · Procesos, hilos y planificación", MODULO1, False),
    ("Módulo 2 · Sincronización: mutex, productor-consumidor, interbloqueo", m2_sincronizacion, False),
    ("Módulo 3 · Memoria: asignación contigua, MMU y reemplazo", m3_memoria, False),
    ("Gráficos de todos los módulos", graficos, False),
    ("Pruebas automáticas (pytest)", pruebas, False),
]


def menu(titulo, opciones, salida):
    """Muestra las opciones, ejecuta la elegida y repite hasta que se elige 0."""
    disponibles = [op for op in opciones if HAY_C or not op[2]]
    ocultas = len(disponibles) < len(opciones)
    while True:
        print(f"\n{'=' * 70}\n  {titulo}\n{'=' * 70}")
        for numero, (texto, _, _) in enumerate(disponibles, start=1):
            print(f"  {numero}. {texto}")
        print(f"  0. {salida}")
        if ocultas:
            print("\n  (Las opciones en C solo aparecen en Linux o WSL)")

        eleccion = input("\nElige una opción: ").strip()
        if eleccion == "0":
            return
        if not eleccion.isdigit() or not 1 <= int(eleccion) <= len(disponibles):
            print(f"  '{eleccion}' no es una opción válida. Escribe un número del 0 al {len(disponibles)}.")
            continue

        texto, accion, _ = disponibles[int(eleccion) - 1]
        if isinstance(accion, list):                # submenú: al salir vuelve aquí
            menu(texto, accion, "Volver al menú principal")
            continue

        print(f"\n{'#' * 70}\n#  {texto}\n{'#' * 70}\n")
        try:
            accion()
        except KeyboardInterrupt:
            print("\n  Interrumpido.")
        except Exception as error:              # un módulo que falla no cierra el menú
            print(f"\n  Error: {type(error).__name__}: {error}")
        input("\nPulsa Enter para volver al menú...")


if __name__ == "__main__":
    try:
        menu("SO-Sim · Hotel Las Estrellas", OPCIONES, "Salir")
        print("Hasta luego.")
    except (KeyboardInterrupt, EOFError):
        print("\nHasta luego.")
