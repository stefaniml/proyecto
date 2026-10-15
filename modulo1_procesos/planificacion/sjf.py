"""SJF — entre los huéspedes ya presentes, primero el trámite más corto."""


def elegir(cola):
    # ELIGE POR DURACIÓN: el trámite más corto
    return min(cola, key=lambda f: f.duracion)
