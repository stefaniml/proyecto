#!/usr/bin/env python3
"""SO-Sim · Hotel Las Estrellas — menú principal del simulador.

    python main.py          (Windows)
    python3 main.py         (Linux / WSL)

Muestra un menú numerado; cada opción ejecuta un módulo y al terminar vuelve
al menú. Las opciones en C (fork, exec, wait) solo aparecen en Linux, donde
se compilan solas con gcc o clang la primera vez.

Para añadir un módulo: escribir su función y agregar una línea en OPCIONES.
"""
import os
import shutil
import subprocess
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent
sys.path.insert(0, str(RAIZ))

HAY_C = os.name == "posix"          # Linux / WSL: fork() y exec() existen
CARPETA_C = RAIZ / "modulo1_procesos" / "procesos_hilos"


# ================================================================ utilidades ===
def preguntar(texto, defecto):
    """Pide un valor; con Enter se queda el valor por defecto."""
    respuesta = input(f"  {texto} [{defecto}]: ").strip()
    return respuesta or defecto


def pedir_jornada():
    jornadas = sorted(p.stem for p in (RAIZ / "escenarios").glob("jornada_*.json"))
    jornada = preguntar(f"Jornada ({' / '.join(jornadas)})", "jornada_corta")
    if jornada not in jornadas:
        print(f"  No existe '{jornada}', se usa jornada_corta.")
        jornada = "jornada_corta"
    return jornada


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
    from modulo1_procesos.procesos_hilos import hilos
    hilos.ejecutar()


def m1_planificacion():
    from modulo1_procesos import planificacion
    jornada = pedir_jornada()
    quantum = preguntar("Quantum de Round Robin (minutos)", "4")
    if not quantum.isdigit() or int(quantum) < 1:
        print("  El quantum debe ser un entero positivo, se usa 4.")
        quantum = "4"
    print()
    planificacion.ejecutar(jornada, int(quantum))


def m1_fork_exec():
    """Programa en C: el SO crea procesos reales con fork(), exec() y wait()."""
    if not compilar("atender", "mostrador"):
        return
    jornada = pedir_jornada()
    print()
    sys.stdout.flush()
    subprocess.run([str(CARPETA_C / "mostrador"), f"escenarios/{jornada}.json"], cwd=RAIZ)


# ================================================================== Módulo 2 ===
def m2_sincronizacion():
    import threading
    from modulo2_sincronizacion.interbloqueo import SimulaciónInterbloqueo
    from modulo2_sincronizacion.limpieza import BufferLimpieza
    from modulo2_sincronizacion.registro import RegistroHotel

    print("  Registro de la habitación 302 con 5 recepcionistas a la vez:")
    for usar_mutex in (True, False):
        duplicados = RegistroHotel(usar_mutex).simular_concurrencia(5)
        print(f"    {'con mutex' if usar_mutex else 'sin mutex'}: duplicados = {duplicados}")

    buffer = BufferLimpieza(capacidad=3)
    buffer.simular_productor_consumidor(total_items=10)
    print(f"\n  Productor-consumidor (búfer de 3, 10 habitaciones): "
          f"búfer vacío al final = {buffer.buffer == []}")

    sim = SimulaciónInterbloqueo()
    hilos = [threading.Thread(target=sim.tarea_sin_orden, args=(rol,)) for rol in (True, False)]
    for h in hilos:
        h.start()
    for h in hilos:
        h.join()
    sim.tarea_con_orden_unico()
    print("  Interbloqueo: llave maestra y carrito, sin orden y con orden único -> terminó")


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


# ===================================================================== menú ===
OPCIONES = [            # (texto en el menú, función, ¿necesita C/Linux?)
    ("Módulo 1 · Hilos: el mismo trámite con y sin hilos", m1_hilos, False),
    ("Módulo 1 · Planificación: FCFS, SJF, Round Robin, Prioridad", m1_planificacion, False),
    ("Módulo 1 · Procesos reales en C: fork, exec y wait", m1_fork_exec, True),
    ("Módulo 2 · Sincronización: mutex, productor-consumidor, interbloqueo", m2_sincronizacion, False),
    ("Módulo 3 · Memoria: asignación contigua, MMU y reemplazo", m3_memoria, False),
    ("Gráficos de todos los módulos", graficos, False),
]


def menu():
    disponibles = [op for op in OPCIONES if HAY_C or not op[2]]
    while True:
        print(f"\n{'=' * 70}\n  SO-Sim · Hotel Las Estrellas\n{'=' * 70}")
        for numero, (texto, _, _) in enumerate(disponibles, start=1):
            print(f"  {numero}. {texto}")
        print("  0. Salir")
        if not HAY_C:
            print("\n  (Las opciones en C solo aparecen en Linux o WSL)")

        eleccion = input("\nElige una opción: ").strip()
        if eleccion == "0":
            print("Hasta luego.")
            return
        if not eleccion.isdigit() or not 1 <= int(eleccion) <= len(disponibles):
            print(f"  '{eleccion}' no es una opción válida. Escribe un número del 0 al {len(disponibles)}.")
            continue

        texto, funcion, _ = disponibles[int(eleccion) - 1]
        print(f"\n{'#' * 70}\n#  {texto}\n{'#' * 70}\n")
        try:
            funcion()
        except KeyboardInterrupt:
            print("\n  Interrumpido.")
        except Exception as error:              # un módulo que falla no cierra el menú
            print(f"\n  Error: {type(error).__name__}: {error}")
        input("\nPulsa Enter para volver al menú...")


if __name__ == "__main__":
    try:
        menu()
    except (KeyboardInterrupt, EOFError):
        print("\nHasta luego.")
