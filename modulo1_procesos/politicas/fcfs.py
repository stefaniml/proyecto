"""FCFS — primero en llegar, primero en ser atendido. No expropiativo."""
EXPROPIATIVA = False


def elegir(cola):
    return min(cola, key=lambda f: (f.llegada, f.pid))
