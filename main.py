#!/usr/bin/env python3
"""SO-Sim · Hotel Las Estrellas — orden única del simulador.

    python main.py                         todos los módulos y luego los gráficos
    python main.py 1                       Módulo 1 completo
    python main.py 1 planificacion         solo una parte (planificacion | hilos)
    python main.py 1 planificacion --jornada jornada_dia --quantum 2
    python main.py graficos                solo los gráficos de todos los módulos

Cada módulo expone una función ejecutar() y se registra en MODULOS.
"""
import argparse
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def modulo1(args):
    from modulo1_procesos import ejecutar
    ejecutar(args.parte or "todo", args.jornada, args.quantum)


def graficos(args):
    from analisis import graficos
    print(f"\n{'#' * 78}\n#  GRÁFICOS · figuras de todos los módulos\n{'#' * 78}\n")
    graficos.ejecutar()


MODULOS = {"1": modulo1}       # cada módulo añade aquí su función


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
