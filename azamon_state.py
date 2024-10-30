from __future__ import annotations

from aima . search import hill_climbing, simulated_annealing
import random
from cmath import log
from typing import List, Set, Generator

from azamon_operators import AzamonOperator, MoveParcel, Swap_2smalls_1big, SwapParcels
from azamon_problem_parameters import ProblemParameters
from abia_azamon import *
from copy import deepcopy


class StateRepresentation(object):
    def __init__(self, params: ProblemParameters, v_o: List[Set[int]]):
        self.params = params
        self.v_o = v_o
        self.contador = 0

    def copy(self) -> StateRepresentation:
        # Afegim el copy per cada set!
        v_o_copy = [set_i.copy() for set_i in self.v_o]
        return StateRepresentation(self.params, v_o_copy)

    def detalles(self) -> StateRepresentation:
        for oferta_id in range(len(self.v_o)):
            print(oferta_id,self.params.ofertas[oferta_id])
            peso=0.0
            for paquete_id in self.v_o[oferta_id]:
                print(paquete_id,self.params.packages[paquete_id])
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
    


    def generate_actions(self) -> Generator[AzamonOperator, None, None]:
        

        def asignable(prioridad, dias):
            return not ((prioridad != 0 or dias != 1)
                        and (prioridad != 1 or dias != 2)
                        and (prioridad != 1 or dias != 3)
                        and (prioridad != 2 or dias != 4)
                        and (prioridad != 2 or dias != 5))
        



        maxWeight = []
        for oferta_id in range(len(self.v_o)):
            maxWeight.append([self.params.ofertas[oferta_id].pesomax, self.params.ofertas[oferta_id].dias])
        #print(maxWeight)
        free_spaces = maxWeight

        for oferta_id in range(len(self.v_o)):
            for paquete_id in self.v_o[oferta_id]:
                free_spaces[oferta_id][0] -= self.params.packages[paquete_id].peso
        #print(free_spaces)

        for oferta_id in range(len(self.v_o)):
            for paquete_id in self.v_o[oferta_id]:
                prioridad_paq = self.params.packages[paquete_id].prioridad
                dias_paq = ()
                if prioridad_paq == 0:
                    dias_paq = (1,)
                if prioridad_paq == 1:
                    dias_paq = (1,2,3)
                if prioridad_paq == 2:
                    dias_paq = (1,2,3,4,5)
                
                #Generar los movimientos posibles de los paquetes
                for i in range(len(self.v_o)):
                    #print(dias_paq)
                    if self.params.packages[paquete_id].peso <= free_spaces[i][0] and self.params.ofertas[i].dias in dias_paq:
                        if i != oferta_id:
                            #print('generate_actions: voy a mover',paquete_id,oferta_id,i)
                            yield MoveParcel(paquete_id,oferta_id,i)   
                
                #Generar los intercambios posibles entre los paquetes
                for i in range(len(self.v_o)):
                    for p_id in self.v_o[i]:
                        if paquete_id != p_id and oferta_id != i:
                            prioridad_paq1 = self.params.packages[p_id].prioridad
                            dias_paq1 = ()
                            if prioridad_paq1 == 0:
                                dias_paq1 = (1,)
                            if prioridad_paq1 == 1:
                                dias_paq1 = (1,2,3)
                            if prioridad_paq1 == 2:
                                dias_paq1 = (1,2,3,4,5) 

                            #print(self.params.ofertas[i].dias,dias_paq,self.params.ofertas[oferta_id].dias, dias_paq1)

                            if self.params.ofertas[i].dias in dias_paq and self.params.ofertas[oferta_id].dias in dias_paq1:
                                #print(free_spaces[oferta_id][0],self.params.packages[paquete_id].peso,self.params.packages[p_id].peso,free_spaces[i][0] ,self.params.packages[p_id].peso, self.params.packages[paquete_id].peso)
                                if free_spaces[oferta_id][0] + self.params.packages[paquete_id].peso >= self.params.packages[p_id].peso and free_spaces[i][0] + self.params.packages[p_id].peso >= self.params.packages[paquete_id].peso:
                                    #print('generate_actions: voy a swapear',paquete_id, p_id, oferta_id, i)
                                    yield SwapParcels(paquete_id, p_id, oferta_id, i)


                # Generar los intercambios de 2smalls 1 big
                for o in range(len(self.v_o)): # mirar en otra oferta
                    if oferta_id != o: # que no sea la misma oferta
                        list_paq=list(self.v_o[o]) # hacer una lista del set, con los id de los paquetes del set
                        #print ("swap2: ", oferta_id, paquete_id, o, list_paq)
                        for i in range(len(list_paq)): # por un paquete
                            for j in range(i,len(list_paq)): #miro todos los paquetes
                                if i != j: # que no sea el mismo paquete
                                    # miro que sean asignables a la otra oferta con función aux asignable()
                                    #print('swap2**',i,list_paq[i],list_paq[j],j,o)
                                    if asignable(self.params.packages[list_paq[i]].prioridad,self.params.ofertas[oferta_id].dias) and asignable(self.params.packages[list_paq[j]].prioridad,self.params.ofertas[oferta_id].dias) and  asignable(self.params.packages[paquete_id].prioridad,self.params.ofertas[o].dias):
                                        # miro si al quitar los dos paquetes de la oferta cabe el paquete grande y viceversa
                                        if (free_spaces[oferta_id][0] + self.params.packages[paquete_id].peso >= self.params.packages[list_paq[i]].peso + self.params.packages[list_paq[j]].peso) and (free_spaces[o][0] + self.params.packages[list_paq[i]].peso + self.params.packages[list_paq[j]].peso >= self.params.packages[paquete_id].peso):
                                            #print('generate_actions: voy a swapear2',list_paq[i],list_paq[j],paquete_id,o,oferta_id)
                                            #print('generate_actions: detalles')
                                            #print (self.detalles())
                                            #print('generate_actions: fin detalles')
                                            yield Swap_2smalls_1big(list_paq[i],list_paq[j],paquete_id,o,oferta_id)

    def apply_action(self, action: AzamonOperator) -> StateRepresentation:
        new_state = self.copy()

        
        if isinstance(action, MoveParcel):
            p_i = action.p_i
            c_j = action.c_j
            c_k = action.c_k

            new_state.v_o[c_k].add(p_i)
            new_state.v_o[c_j].remove(p_i)

            #print("MOVED ", p_i ,"-> Contenedor ", c_k, new_state.v_o[c_k],",", c_j, new_state.v_o[c_j])

       
        elif isinstance(action, SwapParcels):
            p_i = action.p_i
            p_j = action.p_j

            c_i = action.c_i
            c_j = action.c_j

            new_state.v_o[c_j].add(p_i)
            new_state.v_o[c_i].remove(p_i)

            new_state.v_o[c_i].add(p_j)
            new_state.v_o[c_j].remove(p_j)

            #print("SWAPPED ", p_i, " y ", p_j ,"-> ", new_state.v_o[c_i], new_state.v_o[c_j])

        elif isinstance(action, Swap_2smalls_1big):
            p_i = action.p_i
            p_j = action.p_j
            p_g = action.p_g

            c_ij = action.c_ij
            c_g = action.c_g
            #print("SWAPPED2 ", p_i, p_j," y ", p_g ,"-> ", new_state.v_o[c_ij], new_state.v_o[c_g])
            
            new_state.v_o[c_g].add(p_i)
            new_state.v_o[c_g].add(p_j)
            new_state.v_o[c_ij].remove(p_i)
            new_state.v_o[c_ij].remove(p_j)

            new_state.v_o[c_ij].add(p_g)
            new_state.v_o[c_g].remove(p_g)
            


        self.contador += 1 
            
        return new_state
    
    def generate_one_action(self) -> Generator[AzamonOperator, None, None]:
        
        maxWeight = []
        for oferta_id in range(len(self.v_o)):
            maxWeight.append([self.params.ofertas[oferta_id].pesomax, self.params.ofertas[oferta_id].dias])
        #print(maxWeight)
        free_spaces = maxWeight

        for oferta_id in range(len(self.v_o)):
            for paquete_id in self.v_o[oferta_id]:
                free_spaces[oferta_id][0] -= self.params.packages[paquete_id].peso
        #print(free_spaces)

        for oferta_id in range(len(self.v_o)):
            for paquete_id in self.v_o[oferta_id]:
                prioridad_paq = self.params.packages[paquete_id].prioridad
                dias_paq = ()
                if prioridad_paq == 0:
                    dias_paq = (1,)
                if prioridad_paq == 1:
                    dias_paq = (1,2,3)
                if prioridad_paq == 2:
                    dias_paq = (1,2,3,4,5)
                
                #Generar los movimientos posibles de los paquetes
                move_parcel_combinations = set()
                for i in range(len(self.v_o)):
                    #print(dias_paq)
                    if self.params.packages[paquete_id].peso <= free_spaces[i][0] and self.params.ofertas[i].dias in dias_paq:
                        if i != oferta_id:
                          move_parcel_combinations.add((paquete_id,oferta_id,i))     
                
                #Generar los intercambios posibles entre los paquetes
                swap_parcels_combinations = set()
                for i in range(len(self.v_o)):
                    for p_id in self.v_o[i]:
                        if paquete_id != p_id and oferta_id != i:
                            prioridad_paq1 = self.params.packages[p_id].prioridad
                            dias_paq1 = ()
                            if prioridad_paq1 == 0:
                                dias_paq1 = (1,)
                            if prioridad_paq1 == 1:
                                dias_paq1 = (1,2,3)
                            if prioridad_paq1 == 2:
                                dias_paq1 = (1,2,3,4,5) 
                            
                            if self.params.ofertas[i].dias in dias_paq and self.params.ofertas[oferta_id] in dias_paq1:
                                if free_spaces[oferta_id][0] + self.params.packages[paquete_id].peso >= self.params.packages[p_id].peso and free_spaces[i][0] + self.params.packages[p_id].peso >= self.params.packages[paquete_id].peso  :
                                    swap_parcels_combinations.add(paquete_id, p_id)
      
               
                                            
       
        n = len(move_parcel_combinations)
        m = len(swap_parcels_combinations)
        
        random_value = random.random()
        if random_value < (n / (n + m)):
            combination = random.choice(list(move_parcel_combinations))
            yield MoveParcel(combination[0], combination[1], combination[2])
        else:
            combination = random.choice(list(swap_parcels_combinations))
            yield SwapParcels(combination[0], combination[1])

    def heuristic1(self) -> float:
        return self.calcular_cost()
    
    def heuristic2(self) -> float:
        weight_happiness = 0.8  
        cost = self.calcular_cost()  
        happiness = self.happiness() 
        return cost - (weight_happiness * happiness)
    
    def heuristic3(self) -> float:
        h=0.0
        for oferta_id in range(len(self.v_o)):
            sum = 0.0
            for paquete_id in self.v_o[oferta_id]:
                sum += self.params.packages[paquete_id].peso
                occupancy = sum/self.params.ofertas[oferta_id].pesomax
                #print('o',occupancy)
            h+=(occupancy)*log(occupancy)
            #print('h',h)
            h=h.real
            #print('h',h)
        return -h
    
    def heuristic4(self) -> float:
        pass


    def calcular_cost(self):
        #print(self.v_o)
        cost = 0.0
        for elem in range(len(self.v_o)):
            if len(self.v_o[elem]) > 0:
                for id_paq in self.v_o[elem]:
                    cost += self.params.packages[id_paq].peso*self.params.ofertas[elem].precio
                    if self.params.ofertas[elem].dias == 3 or self.params.ofertas[elem].dias == 4:
                        cost += 0.25*self.params.packages[id_paq].peso
                    if self.params.ofertas[elem].dias == 5:
                        cost += 0.5*self.params.packages[id_paq].peso       
        #print("***************")          
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
    


def generate_initial_state(params: ProblemParameters, sol) -> StateRepresentation:
    if sol == 1:
        return StateRepresentation(params, crear_asignacion_1(params.packages,params.ofertas))
    
    if sol == 2:
        return StateRepresentation(params, crear_asignacion_2(params.packages,params.ofertas))


def crear_asignacion_1(l_paquetes, l_ofertas):

    def assignar1(lst,n_ofertas):
        v_o=[set() for _ in range(n_ofertas)]
        #print(v_o)
        
        for paquete_id in range(len(lst)):
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
            #print('antes de if',l_ofertas[id_oferta],id_oferta)
            if precio_min > l_ofertas[id_oferta].precio and asignable(prioridad,l_ofertas[id_oferta]):
                #print('bucle')
                l_ofertas[id_oferta].precio
                precio_min = l_ofertas[id_oferta].precio
                id_oferta_min=id_oferta
        #print ('fuera del bucle',precio_min,id_oferta_min)
        if id_oferta_min == -1:
            print("Esta situación no se debería dar.")
            #raise ValueError
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
            #print('asigancion',l_ofertas[oferta_potencial],l_paquetes[id_paquete],peso_por_oferta[oferta_potencial] )
            if l_paquetes[id_paquete].peso + peso_por_oferta[oferta_potencial] <= l_ofertas[oferta_potencial].pesomax:
                peso_por_oferta[oferta_potencial] = peso_por_oferta[oferta_potencial]  + l_paquetes[id_paquete].peso
                oferta_por_paquete[id_paquete] = oferta_potencial
                paquete_asignado = True
                
            else:
                copia_ofertas.remove(id_oferta_potencial)
    """
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
    """
    v_o = assignar1(oferta_por_paquete, len(l_ofertas))
    return v_o


def crear_asignacion_2 (l_paq, l_ofe):  
    def assignable (paq = Paquete, dies = int): #Definim les condicions que ha de tenir cada Paquet en funció de la seva prioritat
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
        
        for i in range(len(l_paq)): #Dividim els paquets en tres llistes, una per cada prioritat
            if l_paq[i].prioridad == 0:
                prio0.append((l_paq[i], i)) #Ens guardem la instància de Paquet i el seu índex a la llista original abans d'ordenar-la amb una tupla
            elif l_paq[i].prioridad == 1:
                prio1.append((l_paq[i], i))
            elif l_paq[i].prioridad == 2:
                prio2.append((l_paq[i], i))

        res = (prio0, prio1, prio2) #Juntem les tres llistes en una tupla
        return res 

    def assignar(l_paquets = list[Paquete], l_ofe = list[Oferta]):
        l_paq = ordenar(l_paquets)
        l_ofe_copy = deepcopy(l_ofe) #Fem una còpia per no modificar l'original
        lst = [set() for _ in range (len(l_ofe_copy))] #Creem una llista de sets
        for i in range(3):
            for _ in range(len(l_paq[i])): #Recorrem la llista de paquets ordenada
                id_paquet = max(l_paq[i], key=lambda x: x[1])
                l_paq[i].remove(id_paquet)
                for ofert in range(len(l_ofe_copy)):
                    if id_paquet[0].peso <= l_ofe_copy[ofert].pesomax and assignable(id_paquet[0], l_ofe_copy[ofert].dias): #Comprovem que el pes disponible de la oferta és menor al del paquet i els dies d'entrega estan dins de la prioritat del paquet
                        lst[ofert].add(id_paquet[1]) #Afegim l'índex del paquet al set de la oferta
                        l_ofe_copy[ofert].pesomax -= id_paquet[0].peso #Restem el pes del paquet al pes disponible de l'oferta
                        break #Passem al següent paquet

        llargada = 0 #Comprovem que tots els paquets han sigut assignats
        for e in lst:
            llargada += len(e)
        if llargada != len(l_paquets):
            return 'No hi ha resposta'
        else:
            return lst
    v_o = assignar(l_paq, l_ofe)
    return v_o #Retornem la llista de sets amb els índexsos dels paquets