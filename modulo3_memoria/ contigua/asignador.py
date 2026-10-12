class AsignadorContiguo:
    """Simula la asignación de memoria contigua (Primer, Mejor y Peor Ajuste)."""
    
    def __init__(self, total_memoria):
        # Representamos la memoria como una lista de booleanos: False (Libre), True (Ocupado)
        self.memoria = [False] * total_memoria
        self.total_memoria = total_memoria

    def _buscar_bloques_libres(self):
        """Devuelve una lista de tuplas (indice_inicio, tamaño_bloque) de los espacios libres."""
        bloques = []
        inicio = -1
        tamano = 0
        
        for i in range(self.total_memoria):
            if not self.memoria[i]:  # Si está libre
                if inicio == -1:
                    inicio = i
                tamano += 1
            else:  # Si está ocupado
                if inicio != -1:
                    bloques.append((inicio, tamano))
                    inicio = -1
                    tamano = 0
                    
        # Añadir el último bloque si llega al final
        if inicio != -1:
            bloques.append((inicio, tamano))
            
        return bloques

    def asignar_primer_ajuste(self, tamano_solicitado):
        """Asigna el primer bloque libre que sea lo suficientemente grande."""
        bloques = self._buscar_bloques_libres()
        for inicio, tamano in bloques:
            if tamano >= tamano_solicitado:
                self._ocupar_memoria(inicio, tamano_solicitado)
                return inicio, "Asignado (Primer Ajuste)"
        
        return -1, "Fallo: Fragmentación Externa"

    def asignar_mejor_ajuste(self, tamano_solicitado):
        """Asigna el bloque libre más pequeño que sea suficiente (deja el hueco más chico)."""
        bloques = self._buscar_bloques_libres()
        # Ordenar bloques por tamaño ascendente
        bloques.sort(key=lambda x: x[1])
        
        for inicio, tamano in bloques:
            if tamano >= tamano_solicitado:
                self._ocupar_memoria(inicio, tamano_solicitado)
                return inicio, "Asignado (Mejor Ajuste)"
                
        return -1, "Fallo: Fragmentación Externa"

    def _ocupar_memoria(self, inicio, tamano):
        """Marca las habitaciones como ocupadas."""
        for i in range(inicio, inicio + tamano):
            self.memoria[i] = True

    def liberar_memoria(self, inicio, tamano):
        """Libera un bloque contiguo de habitaciones (Check-out)."""
        for i in range(inicio, inicio + tamano):
            self.memoria[i] = False
