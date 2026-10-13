"""Prioridad — primero el de mayor prioridad (1 = la más alta). No expropiativo."""
EXPROPIATIVA = False


def elegir(cola):
    return min(cola, key=lambda f: (f.prioridad, f.llegada, f.pid))
