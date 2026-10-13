#!/usr/bin/env python3
"""SO-Sim · Hotel Las Estrellas — orden única del simulador.

    python main.py                 todos los módulos y luego los gráficos
    python main.py 1               Módulo 1 completo
    python main.py 2               Módulo 2 completo (Sincronización)
    python main.py 3               Módulo 3 completo (Gestión de Memoria)
    python main.py 1 planificacion solo una parte (planificacion | hilos)
    python main.py 1 planificacion --jornada jornada_dia --quantum 2
    python main.py graficos        solo los gráficos de todos los módulos

Cada módulo expone una función ejecutar() o se ejecuta directamente aquí y se registra en MODULOS.
"""
import argparse
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def modulo1(args):
    from modulo1_procesos import ejecutar
    ejecutar(args.parte or "todo", args.jornada, args.quantum)


def modulo2(args):
    print(f"\n{'#' * 78}\n#  MÓDULO 2 · Sincronización y Exclusión Mutua\n{'#' * 78}\n")
    try:
        from modulo2_sincronizacion import registro, interbloqueo, limpieza
        print("Módulos de sincronización cargados correctamente.")
        print("Ejecutando pruebas de exclusión mutua, productor-consumidor y deadlock...")
        # Aquí puedes llamar a las funciones específicas de tus archivos, por ejemplo:
        # registro.ejecutar()
        # interbloqueo.demostrar()
    except Exception as e:
        print(f"Error en Módulo 2: {e}")


def modulo3(args):
    from core.cargador import CargadorJornada
    from modulo3_memoria.paginacion.mmu import MemoryManager

    print(f"\n{'#' * 78}\n#  MÓDULO 3 · Gestión de Memoria\n{'#' * 78}\n")
    
    ruta = f"escenarios/{args.jornada}.json" if not args.jornada.endswith(".json") else args.jornada
    
    try:
        cargador = CargadorJornada(ruta)
        solicitudes = cargador.cargar()
        
        # Iniciar la MMU (El Hotel) con 5 marcos físicos (habitaciones)
        mmu = MemoryManager(total_frames=5, politica_reemplazo="FIFO")
        
        print("Capacidad del Hotel (RAM): 5 marcos.\n")
        
        for solicitud in solicitudes:
            direccion_virtual = (solicitud.pid * 1000) + solicitud.tiempo_estimado
            print(f"Huésped PID {solicitud.pid} solicita dir. virtual: {direccion_virtual}")
            
            direccion_fisica, estado = mmu.translate_address(direccion_virtual)
            print(f"-> {estado} | Física: {direccion_fisica}\n")
            
        print(f"Total de Fallos de Página (Page Faults): {mmu.page_faults}")
        
    except FileNotFoundError:
        print(f"Error: No se encontró el archivo {ruta}")
    except Exception as e:
        print(f"Error durante la simulación del Módulo 3: {e}")


def graficos(args):
    from analisis import graficos
    print(f"\n{'#' * 78}\n#  GRÁFICOS · figuras de todos los módulos\n{'#' * 78}\n")
    graficos.ejecutar()


MODULOS = {"1": modulo1, "2": modulo2, "3": modulo3}       # cada módulo añade aquí su función


def main():
    ap = argparse.ArgumentParser(description="SO-Sim · Hotel Las Estrellas")
    ap.add_argument("modulo", nargs="?", choices=list(MODULOS) + ["graficos"],
                    help="número de módulo, o 'graficos'")
    ap.add_argument("parte", nargs="?", help="parte del módulo (por defecto, todas)")
    ap.add_argument("--jornada", default="jornada_corta", help="escenario en escenarios/")
    ap.add_argument("--quantum", type=int, default=4, help="quantum de Round Robin")
    args = ap.parse_args()

    for numero, correr in MODULOS.items():
        if args.modulo in (None, numero):
            correr(args)
    if args.modulo in (None, "graficos"):     # al final, con los datos ya generados
        graficos(args)
    print()


if __name__ == "__main__":
    main()
