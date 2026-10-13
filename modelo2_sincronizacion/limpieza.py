import threading
import time

class BufferLimpieza:
    def __init__(self, capacidad: int = 5):
        self.capacidad = capacidad
        self.buffer = []
        self.mutex = threading.Lock()
        self.vacios = threading.Semaphore(capacidad)
        self.llenos = threading.Semaphore(0)

    def productor(self, habitacion_id: int):
        self.vacios.acquire()
        with self.mutex:
            self.buffer.append(habitacion_id)
        self.llenos.release()

    def consumidor(self) -> int:
        self.llenos.acquire()
        with self.mutex:
            item = self.buffer.pop(0)
        self.vacios.release()
        return item

    def simular_productor_consumidor(self, total_items: int = 10):
        def produccion():
            for i in range(total_items):
                self.productor(i)
                time.sleep(0.001)

        def consumo():
            for _ in range(total_items):
                self.consumidor()
                time.sleep(0.001)

        tp = threading.Thread(target=produccion)
        tc = threading.Thread(target=consumo)
        tp.start(); tc.start()
        tp.join(); tc.join()
