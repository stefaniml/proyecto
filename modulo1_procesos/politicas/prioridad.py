"""Prioridad — primero el huésped de mayor prioridad (1 = la más alta)."""


def elegir(cola):
    # ELIGE POR PRIORIDAD: el número más bajo (1 = el más urgente)
    return min(cola, key=lambda f: f.prioridad)
