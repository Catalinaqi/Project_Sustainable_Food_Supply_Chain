from dataclasses import dataclass
import datetime

@dataclass
class OperazioneEstesaModel:

    id_operazione: int
    nome_operazione: str
    data_operazione: datetime
    id_prodotto : int
    nome_prodotto : str
    quantita_prodotto : int
    consumo_co2 : float
    

    
   
