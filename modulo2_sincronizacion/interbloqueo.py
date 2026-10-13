import threading

class SimulaciónInterbloqueo:
    def __init__(self):
        self.llave_maestra = threading.Lock()
        self.carrito_servicio = threading.Lock()

    def tarea_sin_orden(self, es_recepcion: bool):
        # Asignación desordenada -> Puede generar Deadlock
        r1 = self.llave_maestra if es_recepcion else self.carrito_servicio
        r2 = self.carrito_servicio if es_recepcion else self.llave_maestra
        if r1.acquire(timeout=0.1):
            if r2.acquire(timeout=0.1):
                r2.release()
            r1.release()

    def tarea_con_orden_unico(self):
        # Asignación ordenada estricta -> Previene Deadlock
        with self.llave_maestra:
            with self.carrito_servicio:
                pass
