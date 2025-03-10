import datetime
from dataclasses import dataclass


@dataclass
class OperationModel:
    """
    Data model for transporting product information between layers.
    """
    Id_operazione: int
    Id_prodotto: int
    Nome_azienda: str
    None_prodotto: str
    Data_operazione: datetime
    Consumo_co2_operazione: float
    Data_operazione: datetime
    Nome_operazione: str
    Quantita_prodotto: float
