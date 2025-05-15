import datetime
from dataclasses import dataclass


@dataclass
class OperationModel:
    """
    Data model for transporting product information between layers.
    """
    id_operazione: int
    id_prodotto: int
    quantita_prodotto: float
    nome_prodotto: str
    data_operazione: datetime
    consumo_co2_operazione: float
    nome_operazione: str
    nome_azienda: str
   
