from __future__ import annotations

from typing import List, Set, Generator

from azamon_operators import BinPackingOperator, MoveParcel, SwapParcels
from azamon_problem_parameters import ProblemParameters
from abia_azamon import *

class StateRepresentation(object):
    def __init__(self, params: ProblemParameters, v_o: List[Set[int]]):
        self.params = params
        self.v_o = v_o

    def copy(self) -> StateRepresentation:
        # Afegim el copy per cada set!
        v_o_copy = [set_i.copy() for set_i in self.v_o]
        return StateRepresentation(self.params, v_o_copy)

    def __repr__(self) -> str:
        return f"v_o={str(self.v_o)} | {self.params}"

    # Utilitzarem aquesta funció auxiliar per trobar l'oferta
    # que conté un paquet determinat
    def find_offer(self, p_i: int) -> int:
        for o_i in range(len(self.v_o)):
            if p_i in self.v_o[o_i]:
                return o_i

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


def generate_initial_state(params: ProblemParameters) -> StateRepresentation:
    ofertas_x_paquete = crear_asignacion_1(params.packages, params.ofertas)
    #print (ofertas_x_paquete)

    v_o=[set() for _ in range(len(params.ofertas))]
    print(v_o)
    for paquete_id in range(len(params.packages)-1):
        v_o[ofertas_x_paquete[paquete_id]].add(paquete_id)

    return StateRepresentation(params, v_o)

def crear_asignacion_1(l_paquetes, l_ofertas):
    def asignable(prioridad, oferta):
        return not ((prioridad != 0 or oferta.dias != 1)
                    and (prioridad != 1 or oferta.dias != 2)
                    and (prioridad != 1 or oferta.dias != 3)
                    and (prioridad != 2 or oferta.dias != 4)
                    and (prioridad != 2 or oferta.dias != 5))
    
    def precio_min(l_ofertas,l_id_ofertas, prioridad):
        #print('precio_min=',l_ofertas,l_id_ofertas, prioridad)
        precio_min = 10000
        id_oferta_min = -1
        for id_oferta in l_id_ofertas:
            #print('hello')
            #print(l_ofertas[id_oferta].precio,l_ofertas[id_oferta].dias, id_oferta)
            #print(precio_min,l_ofertas[id_oferta].precio)
            if precio_min > l_ofertas[id_oferta].precio and asignable(prioridad,l_ofertas[id_oferta]):
                #print('bucle')
                precio_min = l_ofertas[id_oferta].precio
                id_oferta_min=id_oferta
        #print (precio_min,id_oferta_min)
        if id_oferta_min == -1:
            print("Esta situación no se debería dar.")
            raise RuntimeError
        
        return id_oferta_min

    oferta_por_paquete = [0] * len(l_paquetes)
    peso_por_oferta = [0.0] * len(l_ofertas)
    copia_ofertas = []

    for id_oferta in range(len(l_ofertas)):
        copia_ofertas.append(id_oferta)   

    #print(copia_ofertas)
    for id_paquete in range(len(l_paquetes)):
        
        paquete_asignado = False   
        while not paquete_asignado:
            #print(id_paquete)
            #print(l_paquetes[id_paquete].prioridad)
            #print(l_paquetes[id_paquete].peso)
            id_oferta_potencial = precio_min(l_ofertas,copia_ofertas,l_paquetes[id_paquete].prioridad)
            oferta_potencial = id_oferta_potencial
            
            if l_paquetes[id_paquete].peso + peso_por_oferta[oferta_potencial] <= l_ofertas[oferta_potencial].pesomax:
                peso_por_oferta[oferta_potencial] = peso_por_oferta[oferta_potencial]  + l_paquetes[id_paquete].peso
                oferta_por_paquete[id_paquete] = oferta_potencial
                paquete_asignado = True
                print(f"Paq= {id_paquete} Env={oferta_potencial}")
            else:
                copia_ofertas.remove(id_oferta_potencial)
    print()
    for id_paquete in range(len(l_paquetes)):
        print(f"Paq= {id_paquete} Env={oferta_por_paquete[id_paquete]}"
              f" P={l_paquetes[id_paquete].prioridad}"
              f" D={l_ofertas[oferta_por_paquete[id_paquete]].dias}")
    coste_total = 0
    for id_oferta in range(len(l_ofertas)):
        print(f"Env= {id_oferta}"
              f" Weight={peso_por_oferta[id_oferta]}"
              f" MXweight={l_ofertas[id_oferta].pesomax}"
              f" Price={l_ofertas[id_oferta].precio}"
              f" Dias={l_ofertas[id_oferta].dias}")
        
        coste_total = coste_total + peso_por_oferta[id_oferta]*l_ofertas[id_oferta].precio
        if l_ofertas[id_oferta].pesomax < peso_por_oferta[id_oferta]:
            print("Esta situación no se debería dar. ¡Reportadlo!")
            raise RuntimeError
    print(coste_total)  
    return oferta_por_paquete




if __name__ == '__main__':
    npaq = int(input("Numero de paquetes:"))
    semilla = int(input("Semilla aleatoria: "))
    paquetes = random_paquetes(npaq, semilla)
    ofertas = random_ofertas(paquetes, 1.2, 1234)

    inspeccionar_paquetes(paquetes)
    inspeccionar_ofertas(ofertas)
    problema = ProblemParameters(ofertas,paquetes)
    print(generate_initial_state(problema))
