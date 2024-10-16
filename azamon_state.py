from __future__ import annotations

from typing import List, Set, Generator

from azamon_operators import BinPackingOperator, MoveParcel, SwapParcels
from azamon_problem_parameters import ProblemParameters
from abia_azamon import *

class StateRepresentation(object):
    ##################################### que es v_c????
    def __init__(self, params: ProblemParameters, v_c: List[Set[int]]):
        self.params = params
        self.v_c = v_c
    
        initial_state = generate_initial_state(params)
        super.__init__(initial_state)
        

    def copy(self) -> StateRepresentation:
        # Afegim el copy per cada set!
        v_c_copy = [set_i.copy() for set_i in self.v_c]
        return StateRepresentation(self.params, v_c_copy)

    def __repr__(self) -> str:
        return f"v_c={str(self.v_c)} | {self.params}"

    # Utilitzarem aquesta funció auxiliar per trobar el contenidor
    # que conté un paquet determinat
    def find_container(self, p_i: int) -> int:
        for c_i in range(len(self.v_c)):
            if p_i in self.v_c[c_i]:
                return c_i

    def generate_actions(self) -> Generator[BinPackingOperator, None, None]:
        # Primer calculem el PES lliure de cada contenidor
        free_spaces = []
        for c_i, parcels in enumerate(self.v_c):
            h_c_i = self.params.h_max
            for p_i in parcels:
                h_c_i = h_c_i - self.params.v_h[p_i]
            free_spaces.append(h_c_i)
        # Recorregut contenidor per contenidor per saber quins paquets podem moure
        for c_j, parcels in enumerate(self.v_c):
            for p_i in parcels:
                for c_k in range(len(self.v_c)):
                    # Condició: oferta diferent i té pes lliure suficient
                    if c_j != c_k and free_spaces[c_k] >= self.params.v_h[p_i]:
                        yield MoveParcel(p_i, c_j, c_k)

        # Intercanviar paquets
        for p_i in range(self.params.p_max):
            for p_j in range(self.params.p_max):
                if p_i != p_j:
                    c_i = self.find_container(p_i)
                    c_j = self.find_container(p_j)

                    if c_i != c_j:
                        h_p_i = self.params.v_h[p_i]
                        h_p_j = self.params.v_h[p_j]

                        # Condició: hi ha espai lliure suficient per fer l'intercanvi
                        # (Espai lliure del contenidor + espai que deixa el paquet >= espai del nou paquet)
                        if free_spaces[c_i] + h_p_i >= h_p_j and free_spaces[c_j] + h_p_j >= h_p_i:
                            yield SwapParcels(p_i, p_j)

    def apply_action(self, action: BinPackingOperator) -> StateRepresentation:
        new_state = self.copy()
        if isinstance(action, MoveParcel):
            p_i = action.p_i
            c_j = action.c_j
            c_k = action.c_k

            new_state.v_c[c_k].add(p_i)
            new_state.v_c[c_j].remove(p_i)

            if len(new_state.v_c[c_j]) == 0:
                del new_state.v_c[c_j]

        elif isinstance(action, SwapParcels):
            p_i = action.p_i
            p_j = action.p_j

            c_i = new_state.find_container(p_i)
            c_j = new_state.find_container(p_j)

            new_state.v_c[c_i].add(p_j)
            new_state.v_c[c_i].remove(p_i)

            new_state.v_c[c_j].add(p_i)
            new_state.v_c[c_j].remove(p_j)

        return new_state

    def heuristic(self) -> float:
        return len(self.v_c)

def inspeccionar_paquetes(l_paquetes):
    # Dada una lista de paquetes, obtener información de
    # cada uno: peso y prioridad.
    peso_por_prioridad = [0.0, 0.0, 0.0]
    paqs_por_prioridad = [0, 0, 0]

    print(" -------- Paquetes  ------------")
    for paquete in l_paquetes:
        peso_por_prioridad[paquete.prioridad] += paquete.peso
        paqs_por_prioridad[paquete.prioridad] += 1
    for prioridad in range(3):
        for paquete in l_paquetes:
            if paquete.prioridad == prioridad:
                print(paquete)
    print("\n")
    for prioridad in range(3):
        print(f"Prioridad {prioridad}"
              f" N paq={paqs_por_prioridad[prioridad]}"
              f" Peso total= {peso_por_prioridad[prioridad]}")


def inspeccionar_ofertas(l_ofertas):
    # Dada una lista de ofertas, extraer información potencialmente
    # interesante: número de ofertas y peso máximo, precio y días de
    # cada oferta.
    ofertas_por_prioridad = [0, 0, 0, 0, 0]
    pesomax_por_prioridad = [0.0, 0.0, 0.0, 0.0, 0.0]

    print("\n -------- Ofertas  ------------")
    print(f"num ofertas = {len(l_ofertas)}\n")
    for oferta in l_ofertas:
        print(oferta)
        ofertas_por_prioridad[oferta.dias - 1] += 1
        dia = oferta.dias - 1
        pesomax_por_prioridad[dia] += oferta.pesomax
    print("\n")
    for dia in range(5):
        print(f"Dia {dia + 1} N ofertas={ofertas_por_prioridad[dia]}"
              f" Peso maximo= {pesomax_por_prioridad[dia]}")
    print()
    
def generate_initial_state(params: ProblemParameters) -> StateRepresentation:
    x = params.ofertas
    print(x)    



