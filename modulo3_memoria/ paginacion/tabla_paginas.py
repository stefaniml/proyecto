class PageTableEntry:
    """Representa un registro en el directorio de la recepción (MMU)."""
    def __init__(self, frame_number=-1, valid=False):
        self.frame_number = frame_number
        self.valid = valid  # Bit V: True si está en RAM (Hotel), False si está en Disco (Bodega)

class TablaPaginas:
    """Gestiona el mapa hash de páginas de un proceso."""
    def __init__(self):
        self.entradas = {} # Mapeo: Numero de Página -> PageTableEntry

    def obtener_entrada(self, page_number):
        return self.entradas.get(page_number, PageTableEntry())

    def actualizar_entrada(self, page_number, frame_number, valid=True):
        self.entradas[page_number] = PageTableEntry(frame_number, valid)
