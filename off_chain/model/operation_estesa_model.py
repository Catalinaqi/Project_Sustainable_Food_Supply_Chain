from dataclasses import dataclass
import datetime
from model.operation_model import OperationModel
from model.product_model import ProductModel

@dataclass
class OperazioneEstesaModel:

    Id_operazione: int
    Nome_operazione: str
    Data_operazione: datetime
    Id_prodotto : int
    Nome_prodotto : str
    Quantita_prodotto : int
    Consumo_CO2 : float
    

    
   
