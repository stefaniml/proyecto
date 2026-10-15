"""Modulo 2 · La pizarra de reservas (condicion de carrera y exclusion mutua).

Varios recepcionistas consultan la misma pizarra y asignan la misma habitacion.
Entre LEER "libre" y ESCRIBIR el nombre hay un hueco: en ese hueco otro
recepcionista puede leer tambien "libre". Los dos creen que esta disponible y
los dos la asignan.

Teoria de la semana 5:
  - ese tramo leer -> decidir -> escribir es la SECCION CRITICA,
  - el error que produce se llama CONDICION DE CARRERA,
  - se evita con EXCLUSION MUTUA: un mutex deja entrar a uno a la vez.

Lo que medimos es cuantas veces se escribio sobre la misma habitacion.
Lo correcto es una sola escritura; cada escritura de mas es una sobreventa.
"""
import threading
import time


class RegistroHotel:
    """La habitacion 302 de la pizarra, con o sin candado."""

    HABITACION = "302"

    def __init__(self, usar_mutex: bool = True):
        self.usar_mutex = usar_mutex
        self.lock = threading.Lock()        # el mutex: una sola llave de la pizarra
        self.pizarra = {self.HABITACION: "libre"}
        self.escrituras = 0
        self._cuenta = threading.Lock()     # solo para llevar la cuenta sin perder datos

    # ----------------------------------------------- la seccion critica ---
    def _reservar(self, recepcionista: int) -> None:
        estado = self.pizarra[self.HABITACION]       # 1. consulta la pizarra
        time.sleep(0.001)                            # 2. el hueco: le hablan, atiende el telefono
        if estado == "libre":                        # 3. decide con lo que leyo hace un rato
            self.pizarra[self.HABITACION] = f"recepcionista {recepcionista}"
            with self._cuenta:
                self.escrituras += 1

    def _turno(self, recepcionista: int) -> None:
        if self.usar_mutex:
            with self.lock:                 # nadie mas entra mientras este dentro
                self._reservar(recepcionista)
        else:
            self._reservar(recepcionista)   # sin candado: entran todos a la vez

    # ------------------------------------------------------ simulacion ---
    def simular(self, recepcionistas: int = 5) -> dict:
        """Lanza N recepcionistas a la vez sobre la misma habitacion."""
        self.pizarra[self.HABITACION] = "libre"
        self.escrituras = 0

        hilos = [threading.Thread(target=self._turno, args=(i,))
                 for i in range(recepcionistas)]
        for h in hilos:
            h.start()
        for h in hilos:
            h.join()

        return {
            "escrituras": self.escrituras,
            "sobreventas": max(0, self.escrituras - 1),
            "asignada_a": self.pizarra[self.HABITACION],
        }

    # Nombre anterior, por si algun script viejo lo sigue llamando.
    def simular_concurrencia(self, num_recepcionistas: int = 5) -> dict:
        return self.simular(num_recepcionistas)
