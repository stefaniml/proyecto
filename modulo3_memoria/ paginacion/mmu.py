class MMU:
    def __init__(self, tamano_pagina: int = 4096):
        self.tamano_pagina = tamano_pagina

    def traducir(self, direccion_virtual: int, tabla_paginas: dict) -> int:
        pagina = direccion_virtual // self.tamano_pagina
        desplazamiento = direccion_virtual % self.tamano_pagina
        
        if pagina not in tabla_paginas:
            raise MemoryError(f"Fallo de página: La página {pagina} no está en RAM.")
            
        marco = tabla_paginas[pagina]
        return (marco * self.tamano_pagina) + desplazamiento
