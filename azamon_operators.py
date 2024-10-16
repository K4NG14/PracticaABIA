class BinPackingOperator(object):
    pass


class MoveParcel(BinPackingOperator):
    def __init__(self, p_i: int, c_j: int, c_k: int):
        self.p_i = p_i
        self.c_j = c_j
        self.c_k = c_k

    def __repr__(self) -> str:
        return f"Move parcel {self.p_i} from container {self.c_j} to container {self.c_k}"


class SwapParcels(BinPackingOperator): # paso por una solucion peor si en vez de swap cambio uno y despues el otro.
    def __init__(self, p_i: int, p_j: int):
        self.p_i = p_i
        self.p_j = p_j

    def __repr__(self) -> str:
        return f"Swap parcels {self.p_i} and {self.p_j}"
