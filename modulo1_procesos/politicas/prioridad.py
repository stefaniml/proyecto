"""Prioridad — primero el huésped de mayor prioridad (1 = la más alta)."""


def elegir(cola):
    # el de prioridad más alta; si empatan, el que llegó primero
    return min(cola, key=lambda f: (f.prioridad, f.llegada, f.pid))
