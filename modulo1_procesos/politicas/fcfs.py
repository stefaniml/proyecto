"""FCFS — se atiende en estricto orden de llegada."""


def elegir(cola):
    # el que llegó primero al lobby
    return min(cola, key=lambda f: (f.llegada, f.pid))
