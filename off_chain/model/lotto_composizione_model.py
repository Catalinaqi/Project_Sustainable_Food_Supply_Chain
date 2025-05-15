from dataclasses import dataclass, field
from typing import Optional, List


@dataclass
class Lotto:
    id_lotto: int
    tipo: str
    quantita: float
    cons_co2: float 
    composizione: List["Composizione"] = field(default_factory=list)
    co2_da_composizione: float = 0.0  
    co2_totale_unitaria: float = 0.0 

    def __init__(self, id_lotto, tipo, quantita, consumo_co2):
        self.id_lotto = id_lotto
        self.tipo = tipo
        self.quantita = quantita
        self.cons_co2 = consumo_co2
        self.composizione = []

    def calcola_co2_lotto(self) -> float: 
        """
        Calcola la CO2 totale unitaria del lotto, aggiornando
        co2_da_composizione e co2_totale_unitaria.
        Restituisce la CO2 totale unitaria.
        """
        self.co2_da_composizione = 0.0 # Resettato prima del ricalcolo
        if self.composizione:
            for comp in self.composizione:
                co2_componente = comp.get_co2_da_quantita_utilizzata()
                self.co2_da_composizione += co2_componente

        if self.quantita > 0: # Evitiamo divisione per zero
            self.co2_totale_unitaria = (
                self.co2_da_composizione + self.cons_co2
            ) / self.quantita
        else:
            self.co2_totale_unitaria = 0.0 

        return self.co2_totale_unitaria
    

@dataclass
class Composizione:
    id_lotto_input: int
    quantita_utilizzata: float
    lotto_input: Optional[Lotto] = None
    def get_co2_da_quantita_utilizzata(self) -> float: # Nome metodo corretto
        """
        Calcola la CO2 consumata attribuibile alla quantità utilizzata di questo componente.
        """
        if isinstance(self.lotto_input, Lotto):
            costo_unitario_input = self.lotto_input.calcola_co2_lotto() 
            return costo_unitario_input * self.quantita_utilizzata
        return 0.0