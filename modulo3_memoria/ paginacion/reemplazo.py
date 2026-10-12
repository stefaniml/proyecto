class GestorReemplazo:
    """Administra las políticas de reemplazo de páginas (FIFO, LRU)."""
    def __init__(self, politica="FIFO"):
        self.politica = politica
        self.cola_fifo = []  # Rastrea el orden de llegada a los marcos

    def registrar_carga(self, frame_number):
        """Registra que un marco acaba de ser ocupado."""
        if self.politica == "FIFO":
            self.cola_fifo.append(frame_number)

    def seleccionar_victima(self):
        """Selecciona qué marco liberar según la política elegida."""
        if self.politica == "FIFO" and self.cola_fifo:
            return self.cola_fifo.pop(0) # Retorna el marco más antiguo
        # Aquí se puede expandir para LRU en el futuro
        return None
