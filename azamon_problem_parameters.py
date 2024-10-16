from typing import List


class ProblemParameters(object):
    def __init__(self, h_max: int, v_h: List[int], p_max: int, c_max: int):
        self.h_max = h_max  # Alçada màxima de tots els contenidors
        self.v_h = v_h      # Alçades de cada paquet, lista de enteros
        self.p_max = p_max  # Màxim número de paquets
        self.c_max = c_max  # Màxim número de contenidors

    def __repr__(self):
        return f"Params(h_max={self.h_max}, v_h={self.v_h}, p_max={self.p_max}, c_max={self.c_max})"