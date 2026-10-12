from modulo3_memoria.paginacion.tabla_paginas import TablaPaginas
from modulo3_memoria.paginacion.reemplazo import GestorReemplazo

class MemoryManager:
    """Simula la Unidad de Gestión de Memoria (MMU) del Hotel Las Estrellas."""
    def __init__(self, total_frames, politica_reemplazo="FIFO"):
        self.PAGE_SIZE = 4096
        self.free_frames = list(range(total_frames))  # Habitaciones vacías
        self.page_faults = 0
        
        self.tabla = TablaPaginas()
        self.reemplazo = GestorReemplazo(politica=politica_reemplazo)

    def translate_address(self, logical_address):
        """Traduce la dirección virtual a física."""
        # 1. Dividir
        page_number = logical_address // self.PAGE_SIZE
        offset = logical_address % self.PAGE_SIZE

        # 2. Consultar Tabla de Páginas
        entrada = self.tabla.obtener_entrada(page_number)
        
        if entrada.valid:
            # CAMINO FELIZ
            physical_address = (entrada.frame_number * self.PAGE_SIZE) + offset
            return physical_address, "Hit (En Memoria)"
        else:
            # FALLO DE PÁGINA
            return self.handle_page_fault(page_number, offset)

    def handle_page_fault(self, page_number, offset):
        """Resuelve el fallo trayendo la página a RAM o aplicando reemplazo."""
        self.page_faults += 1
        
        if self.free_frames:
            # Hay habitaciones libres
            allocated_frame = self.free_frames.pop(0)
        else:
            # Hotel lleno: Buscar víctima
            allocated_frame = self.reemplazo.seleccionar_victima()

        # Actualizar tabla y registrar en el algoritmo de reemplazo
        self.tabla.actualizar_entrada(page_number, allocated_frame, valid=True)
        self.reemplazo.registrar_carga(allocated_frame)

        # Recomponer dirección física
        physical_address = (allocated_frame * self.PAGE_SIZE) + offset
        return physical_address, "Page Fault Resuelto"
