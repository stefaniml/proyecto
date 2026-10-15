"""Round Robin — turnos acotados de mostrador; al agotarse, vuelve a la cola."""


def elegir(cola):
    # ELIGE AL PRIMERO DE LA FILA. El turno rotativo lo hace el motor
    # (planificacion.py): atiende como máximo el quantum y, si no terminó,
    # lo manda al final de la fila.
    return cola[0]
