"""Modulo 2 · El armario de sabanas del piso (productor-consumidor).

La lavanderia deja sabanas limpias en el armario del piso y recepcion las
recoge. El armario tiene un numero fijo de sitios.

Teoria de la semana 5:
  - 'vacios' y 'llenos' son SEMAFOROS CONTADORES: llevan la cuenta de los
    sitios libres y de las sabanas listas,
  - 'mutex' es un SEMAFORO BINARIO: protege la lista mientras se toca,
  - el orden importa: primero se pide el sitio y despues el candado. Al reves
    se quedaria con el candado en la mano esperando un sitio que nadie puede
    liberar, porque para liberarlo hace falta el candado.

Lo que medimos: que no se pierde ni se duplica ninguna sabana, que el armario
nunca pasa de su capacidad, y cuantas veces tuvo que esperar cada uno.
"""
import threading
import time


class BufferLimpieza:
    def __init__(self, capacidad: int = 3):
        self.capacidad = capacidad
        self.buffer = []
        self.mutex = threading.Lock()                  # una sola mano en el armario
        self.vacios = threading.Semaphore(capacidad)   # sitios libres: empieza lleno
        self.llenos = threading.Semaphore(0)           # sabanas listas: empieza en cero

        self.producidos = 0
        self.consumidos = 0
        self.ocupacion_maxima = 0
        self.esperas_lavanderia = 0      # veces que encontro el armario lleno
        self.esperas_recepcion = 0       # veces que lo encontro vacio

    # ------------------------------------------------------- productor ---
    def productor(self, sabana: int) -> None:
        if not self.vacios.acquire(blocking=False):    # mira si hay sitio ahora mismo
            self.esperas_lavanderia += 1               # no hay: le toca esperar
            self.vacios.acquire()
        with self.mutex:
            self.buffer.append(sabana)
            self.producidos += 1
            self.ocupacion_maxima = max(self.ocupacion_maxima, len(self.buffer))
        self.llenos.release()                          # avisa: hay una sabana lista

    # ------------------------------------------------------ consumidor ---
    def consumidor(self) -> int:
        if not self.llenos.acquire(blocking=False):    # mira si hay alguna sabana
            self.esperas_recepcion += 1                # no hay: le toca esperar
            self.llenos.acquire()
        with self.mutex:
            sabana = self.buffer.pop(0)
            self.consumidos += 1
        self.vacios.release()                          # avisa: quedo un sitio libre
        return sabana

    # ------------------------------------------------------ simulacion ---
    def simular(self, total: int = 10) -> dict:
        """La lavanderia deja N sabanas y recepcion recoge las N."""
        self.buffer.clear()
        self.producidos = self.consumidos = 0
        self.ocupacion_maxima = 0
        self.esperas_lavanderia = self.esperas_recepcion = 0
        recogidas = []

        def lavanderia():
            for i in range(total):
                self.productor(i)
                time.sleep(0.002)          # dobla la siguiente sabana

        def recepcion():
            for _ in range(total):
                recogidas.append(self.consumidor())
                time.sleep(0.005)          # sube a la habitacion: es mas lenta

        tp = threading.Thread(target=lavanderia)
        tc = threading.Thread(target=recepcion)
        tp.start(); tc.start()
        tp.join(); tc.join()

        return {
            "producidos": self.producidos,
            "consumidos": self.consumidos,
            "ocupacion_maxima": self.ocupacion_maxima,
            "capacidad": self.capacidad,
            "esperas_lavanderia": self.esperas_lavanderia,
            "esperas_recepcion": self.esperas_recepcion,
            "sin_perdidas": sorted(recogidas) == list(range(total)),
            "armario_vacio": self.buffer == [],
        }

    # Nombre anterior, por si algun script viejo lo sigue llamando.
    def simular_productor_consumidor(self, total_items: int = 10) -> dict:
        return self.simular(total_items)
