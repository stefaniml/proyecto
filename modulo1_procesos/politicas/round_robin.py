"""Round Robin — el primero de la fila atiende un quantum; si no termina,
vuelve al final de la cola. Expropiativo."""
EXPROPIATIVA = True


def elegir(cola):
    return cola[0]
