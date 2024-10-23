class BinPackingOperator(object):
    pass


class MoveParcel(BinPackingOperator):
    def __init__(self, p_i: int, c_j: int, c_k: int):
        self.p_i = p_i
        self.c_j = c_j
        self.c_k = c_k

    def __repr__(self) -> str:
        return f"Moure paquet {self.p_i} d'oferta {self.c_j} a oferta {self.c_k}"


class SwapParcels(BinPackingOperator): # paso por una solucion peor si en vez de swap cambio uno y despues el otro.
    def __init__(self, p_i: int, p_j: int, c_i: int, c_j: int):
        self.p_i = p_i
        self.p_j = p_j
        self.c_i = c_i
        self.c_j = c_j

    def __repr__(self) -> str:
        return f"Intercanvia {self.p_i} i {self.p_j}"
