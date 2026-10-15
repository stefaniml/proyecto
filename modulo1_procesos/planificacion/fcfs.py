"""FCFS — se atiende en estricto orden de llegada."""


def elegir(cola):
    # ELIGE POR LLEGADA: el que llegó primero al lobby
    return min(cola, key=lambda f: f.llegada)
