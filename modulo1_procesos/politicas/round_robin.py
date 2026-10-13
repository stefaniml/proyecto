"""Round Robin — turnos acotados de mostrador; al agotarse, vuelve a la cola."""


def elegir(cola):
    # el primero de la fila; el quantum lo aplica el motor (planificacion.py)
    return cola[0]
