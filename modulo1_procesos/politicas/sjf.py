"""SJF — entre los huéspedes que esperan, el trámite más corto. No expropiativo."""
EXPROPIATIVA = False


def elegir(cola):
    return min(cola, key=lambda f: (f.duracion, f.llegada, f.pid))
