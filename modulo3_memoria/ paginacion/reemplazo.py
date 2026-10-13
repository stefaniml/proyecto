from typing import List

class AlgoritmosReemplazo:
    @staticmethod
    def fifo(secuencia: List[int], marcos_totales: int) -> int:
        marcos = []
        fallos = 0
        for pag in secuencia:
            if pag not in marcos:
                fallos += 1
                if len(marcos) >= marcos_totales:
                    marcos.pop(0)
                marcos.append(pag)
        return fallos

    @staticmethod
    def lru(secuencia: List[int], marcos_totales: int) -> int:
        marcos = []
        fallos = 0
        for pag in secuencia:
            if pag not in marcos:
                fallos += 1
                if len(marcos) >= marcos_totales:
                    marcos.pop(0)
                marcos.append(pag)
            else:
                marcos.remove(pag)
                marcos.append(pag)
        return fallos

    @staticmethod
    def optimo(secuencia: List[int], marcos_totales: int) -> int:
        marcos = []
        fallos = 0
        for i, pag in enumerate(secuencia):
            if pag not in marcos:
                fallos += 1
                if len(marcos) >= marcos_totales:
                    futuro = secuencia[i+1:]
                    indices = []
                    for m in marcos:
                        if m in futuro:
                            indices.append(futuro.index(m))
                        else:
                            indices.append(float('inf'))
                    victima = indices.index(max(indices))
                    marcos.pop(victima)
                marcos.append(pag)
        return fallos
