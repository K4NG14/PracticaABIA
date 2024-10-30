class AzamonOperator(object):
    pass


class MoveParcel(AzamonOperator):
    def __init__(self, p_i: int, c_j: int, c_k: int):
        self.p_i = p_i
        self.c_j = c_j
        self.c_k = c_k

    def __repr__(self) -> str:
        return f"Moure paquet {self.p_i} d'oferta {self.c_j} a oferta {self.c_k}"


class SwapParcels(AzamonOperator): # paso por una solucion peor si en vez de swap cambio uno y despues el otro.
    def __init__(self, p_i: int, p_j: int, c_i: int, c_j: int):
        self.p_i = p_i
        self.p_j = p_j
        self.c_i = c_i
        self.c_j = c_j

    def __repr__(self) -> str:
        return f"Intercanvia {self.p_i} i {self.p_j}"

class Swap_3smalls_1big(AzamonOperator):
    def __init__(self, p_i: int, p_j: int, p_z: int, p_g: int, c_i: int, c_j: int):
        self.p_i = p_i
        self.p_j = p_j
        self.p_z = p_z
        self.p_g = p_g
        self.c_i = c_i
        self.c_j = c_j

    def __repr__(self) -> str:
        return f"Intercanvia {self.p_i, self.p_j, self.p_z} i {self.p_g}"

class Swap_2smalls_1big(AzamonOperator):
    def __init__(self, p_i: int, p_j: int, p_g: int, c_ij: int, c_g: int):
        self.p_i = p_i
        self.p_j = p_j
        self.p_g = p_g
        self.c_ij = c_ij
        self.c_g = c_g

    def __repr__(self) -> str:
        return f"Intercanvia {self.p_i, self.p_j} i {self.p_g}"

class Swap_4smalls_1big(AzamonOperator):
    def __init__(self, p_i: int, p_j: int, p_z: int, p_g: int, p_c: int,c_i: int, c_j: int):
        self.p_i = p_i
        self.p_j = p_j
        self.p_z = p_z
        self.p_c = p_c
        self.p_g = p_g
        self.c_i = c_i
        self.c_j = c_j

    def __repr__(self) -> str:
        return f"Intercanvia {self.p_i, self.p_j, self.p_z, self.p_c} i {self.p_g}"