import datetime
from dataclasses import dataclass


@dataclass
class RichiestaModel:
    """
    Data model for transporting product information between layers.
    """
    Id_richiesta: int
    Id_azienda_richiedente: int
    nome_azienda_richiedente: str
    Id_azienda_ricevente: int
    nome_azienda_ricevente: str
    Id_azienda_trasportatore: int
    nome_azienda_trasportatore: str
    Id_prodotto: int
    nome_prodotto: str
    Quantita: float
    Stato_ricevente: str
    Stato_trasportatore: str
    Data: datetime.datetime
    
   
