class RelojLogico:
    def __init__(self):
        self.tiempo_actual = 0

    def avanzar(self, unidades: int = 1):
        self.tiempo_actual += unidades

    def obtener(self) -> int:
        return self.tiempo_actual

    def reiniciar(self):
        self.tiempo_actual = 0
