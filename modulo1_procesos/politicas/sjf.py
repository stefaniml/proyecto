"""SJF — entre los huéspedes ya presentes, primero el trámite más corto."""


def elegir(cola):
    # el de menor duración; si empatan, el que llegó primero
    return min(cola, key=lambda f: (f.duracion, f.llegada, f.pid))
