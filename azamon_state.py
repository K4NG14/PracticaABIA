from __future__ import annotations

from typing import List, Set, Generator

from azamon_operators import BinPackingOperator, MoveParcel, SwapParcels
from azamon_problem_parameters import ProblemParameters
from abia_azamon import *
from copy import deepcopy


class StateRepresentation(object):
    def __init__(self, params: ProblemParameters, v_o: List[Set[int]]):
        self.params = params
        self.v_o = v_o

    def copy(self) -> StateRepresentation:
        # Afegim el copy per cada set!
        v_o_copy = [set_i.copy() for set_i in self.v_o]
        return StateRepresentation(self.params, v_o_copy)

    def detalles(self) -> StateRepresentation:
        for oferta_id in range(len(self.v_o)-1):
            print(self.params.ofertas[oferta_id])
            peso=0.0
            for paquete_id in self.v_o[oferta_id]:
                print(self.params.packages[paquete_id])
                peso += self.params.packages[paquete_id].peso
            print(peso)

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

    def heuristic1(self) -> float:
        return self.calcular_cost()
    
    def heuristic2(self) -> float:
        return self.calcular_cost()-self.happiness() #hace falta ponerle un peso a happiness
    
    def calcular_cost(self):
        cost = 0
        for elem in range(len(self.v_o)):
            for id_paq in self.v_o[elem]:
                paq = self.params.packages[id_paq]
                cost += paq.peso*self.params.ofertas[elem].precio
                if paq.prioridad == 1:
                    cost += 0.25*paq.peso
                if paq.prioridad == 2:
                    cost += 0.25*paq.peso*2
        return cost
    def happiness(self):
        happy = 0
        for elem in range(len(self.v_o)):
            for id_paq in self.v_o[elem]:
                paq = self.params.packages[id_paq]
                if paq.prioridad == 1:
                    if self.params.ofertas[elem].dias == 1:
                        happy+=1
                if paq.prioridad == 2: 
                    if self.params.ofertas[elem].dias < 4:
                        happy+= 4-self.params.ofertas[elem].dias
        return happy
       

def generate_initial_state(params: ProblemParameters) -> StateRepresentation:
    return StateRepresentation(params, crear_asignacion_1(params.packages,params.ofertas))


def crear_asignacion_1(l_paquetes, l_ofertas):

    def assignar1(lst,n_ofertas):
        v_o=[set() for _ in range(n_ofertas)]
        print(v_o)
        
        for paquete_id in range(len(lst)-1):
            v_o[lst[paquete_id]].add(paquete_id)
        return v_o
    
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

    v_o = assignar1(oferta_por_paquete, len(l_ofertas))
    return v_o

def crear_asignacion_2 (l_paq, l_ofe):  
    def assignable (paq = Paquete, dies = int):
       if paq.prioridad == 0:
           return dies == 1
       if paq.prioridad == 1:
           return dies <= 3
       if paq.prioridad == 2:
           return dies <= 5

    def ordenar(l_paq = list[Paquete]):
        prio0 = []
        prio1 = []
        prio2 = []
        for i in l_paq:
            if i.prioridad == 0:
                prio0.append(i)
            if i.prioridad == 1:
                prio1.append(i)
            if i.prioridad == 2:
                prio2.append(i)

        prio0_ord = sorted(prio0, key=lambda Paquete: Paquete.peso, reverse=True)
        prio1_ord = sorted(prio1, key=lambda Paquete: Paquete.peso, reverse=True)
        prio2_ord = sorted(prio2, key=lambda Paquete: Paquete.peso, reverse=True)
        return prio0_ord + prio1_ord + prio2_ord
    

    def assignar(l_paquets = list[Paquete], l_ofe = list[Oferta]):
        l_paq = ordenar(l_paquets)
        l_ofe_copy= deepcopy(l_ofe)
        #print(l_ofe is l_ofe_copy)
        #print("******",l_ofe, l_ofe_copy)
        lst = [set() for _ in range (len(l_ofe_copy))]
        for id_paquet in range(len(l_paq)):
            for ofert in range(len(l_ofe_copy)): 
                if l_paq[id_paquet].peso <= l_ofe_copy[ofert].pesomax and assignable(l_paq[id_paquet], l_ofe_copy[ofert].dias):
                    lst[ofert].add(id_paquet)
                    l_ofe_copy[ofert].pesomax -= l_paq[id_paquet].peso
                    break
        #print("******",l_ofe, l_ofe_copy)
        print(lst)
        return lst
    
    v_o = assignar(l_paq, l_ofe)
    return v_o



if __name__ == '__main__':
    npaq = int(input("Numero de paquetes:"))
    semilla = int(input("Semilla aleatoria: "))
    paquetes = random_paquetes(npaq, semilla)
    ofertas = random_ofertas(paquetes, 1.2, 1234)

    inspeccionar_paquetes(paquetes)
    inspeccionar_ofertas(ofertas)
    problema = ProblemParameters(ofertas,paquetes)
    estado_inicial = generate_initial_state(problema)
    print(estado_inicial)
    print(estado_inicial.calcular_cost())
    print(estado_inicial.happiness())
    estado_inicial.detalles()

