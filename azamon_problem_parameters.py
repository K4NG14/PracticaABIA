from typing import List
from abia_azamon import random_ofertas,random_paquetes,Paquete,Oferta
#from azamon_state import StateRepresentation


class ProblemParameters(object):
    def __init__(self, ofertas = List[Oferta], packages = List[Paquete]):
        self.ofertas = ofertas  # ofertas de transporte
        self.packages = packages # paquetes a enviar
        

    def __repr__(self):
        return f"Params(ofertas={self.ofertas}, packages={self.packages})"
    

    


    
        
    