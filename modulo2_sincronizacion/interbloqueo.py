"""Modulo 2 · El pasillo de las llaves (interbloqueo y como se rompe).

Cinco huespedes en un pasillo circular. Entre cada par de puertas hay una sola
llave, y cada huesped necesita las dos que tiene a los lados para entrar.
Es el problema de los filosofos comensales con llaves de hotel.

Teoria de la semana 5: hay interbloqueo cuando se cumplen los cuatro
requisitos de Coffman a la vez:
  1. exclusion mutua      una llave la tiene uno solo,
  2. retencion y espera   agarra la izquierda y espera la derecha sin soltarla,
  3. no expropiacion      nadie le puede quitar la llave,
  4. espera circular      cada uno espera al de al lado, en circulo.
Basta con romper UNO. Aqui rompemos el cuarto: el ultimo huesped toma primero
la llave de su derecha, y con eso el circulo deja de cerrarse.

La barrera hace que los cinco arranquen en el mismo instante: sin ella el
interbloqueo saldria unas veces si y otras no.
"""
import threading
import time


class PasilloDeLlaves:
    def __init__(self, huespedes: int = 5, espera_maxima: float = 0.6):
        self.n = huespedes
        self.espera_maxima = espera_maxima          # cuanto aguanta antes de rendirse
        self.llaves = [threading.Lock() for _ in range(huespedes)]
        self.entraron = 0
        self.bloqueados = 0
        self._cuenta = threading.Lock()

    def _huesped(self, i: int, con_orden: bool, barrera: threading.Barrier) -> None:
        izquierda, derecha = i, (i + 1) % self.n

        # Con orden: el ultimo invierte. Se rompe la espera circular.
        if con_orden and i == self.n - 1:
            primera, segunda = derecha, izquierda
        else:
            primera, segunda = izquierda, derecha

        barrera.wait()                              # los cinco salen a la vez
        self.llaves[primera].acquire()
        time.sleep(0.05)                            # todos alcanzan a tomar la primera
        if self.llaves[segunda].acquire(timeout=self.espera_maxima):
            with self._cuenta:
                self.entraron += 1                  # abrio su puerta
            self.llaves[segunda].release()
        else:
            with self._cuenta:
                self.bloqueados += 1                # se quedo esperando al vecino
        self.llaves[primera].release()

    def simular(self, con_orden: bool) -> dict:
        """Lanza los N huespedes a la vez. con_orden=False reproduce el bloqueo."""
        self.entraron = self.bloqueados = 0
        barrera = threading.Barrier(self.n)
        hilos = [threading.Thread(target=self._huesped, args=(i, con_orden, barrera))
                 for i in range(self.n)]
        for h in hilos:
            h.start()
        for h in hilos:
            h.join()
        return {
            "huespedes": self.n,
            "entraron": self.entraron,
            "bloqueados": self.bloqueados,
            "hubo_interbloqueo": self.bloqueados > 0,
        }
