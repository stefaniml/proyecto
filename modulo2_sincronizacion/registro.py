import threading
import time

class RegistroHotel:
    def __init__(self, usar_mutex: bool = True):
        self.habitaciones = {"302": "Libre"}
        self.usar_mutex = usar_mutex
        self.lock = threading.Lock()
        self.duplicados = 0

    def _operacion_reserva(self, id_recepcionista: int):
        if self.usar_mutex:
            with self.lock:
                self._asignar(id_recepcionista)
        else:
            self._asignar(id_recepcionista)

    def _asignar(self, id_recepcionista: int):
        estado = self.habitaciones.get("302")
        time.sleep(0.001)  # Provoca la condición de carrera si no hay candado
        if estado == "Libre":
            self.habitaciones["302"] = f"Asignado por {id_recepcionista}"
        else:
            self.duplicados += 1

    def simular_concurrencia(self, num_recepcionistas: int = 5) -> int:
        self.duplicados = 0
        self.habitaciones["302"] = "Libre"
        hilos = []
        for i in range(num_recepcionistas):
            t = threading.Thread(target=self._operacion_reserva, args=(i,))
            hilos.append(t)
            t.start()
        for t in hilos:
            t.join()
        return self.duplicados
