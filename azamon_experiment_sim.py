from typing import Generator

from aima.search import Problem

from azamon_operators import AzamonOperator
from azamon_state import StateRepresentation
from aima . search import hill_climbing, simulated_annealing
import random
from cmath import log
from typing import List, Set, Generator
from azamon_problem import Azamon
from azamon_operators import AzamonOperator, MoveParcel, SwapParcels
from azamon_problem_parameters import ProblemParameters
from azamon_state import StateRepresentation, generate_initial_state
from abia_azamon import *
from timeit import default_timer as timer

start = timer()
if __name__ == '__main__':
    npaq = int(input("Numero de paquetes:"))
    semilla = int(input("Semilla aleatoria: "))
    paquetes = random_paquetes(npaq, semilla)
    ofertas = random_ofertas(paquetes, 1.2, 1234)
    sol = int(input("Solució inicial (1-Mikel, 2-Elias): "))
    
    
    #inspeccionar_paquetes(paquetes)
    #inspeccionar_ofertas(ofertas)
    problema = ProblemParameters(ofertas,paquetes)
    start = timer()
    estado_inicial = generate_initial_state(problema, sol)
    end = timer()
    print('Tiempo de generación de estado inicial (ms):',(end - start)*1000)
    #print(estado_inicial)
    
    
    #estado_inicial.detalles()
    start = timer()
    n = simulated_annealing ( Azamon( estado_inicial ) )
    end = timer()
    print('Tiempo que tardo en encontrar solución (ms):',(end - start)*1000)
    print ('Pasos: ', n.contador ) # Estat final
    #print ( n.heuristic1() ) # Valor de l’estat final
    
    
    #n.detalles()
    print("Coste sol inicial: " , estado_inicial.calcular_cost())
    print("Coste sol final: " , n.calcular_cost())
    print("Calcul de felicitat inicial: ",estado_inicial.happiness())
    print("Calcul de felicitat final: ",n.happiness())


    #s = simulated_annealing