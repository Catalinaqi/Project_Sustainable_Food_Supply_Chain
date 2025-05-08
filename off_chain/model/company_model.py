from dataclasses import dataclass
from typing import Optional
import datetime


@dataclass
class CompanyModel:
    """
    Data model for transporting company information between layers.
    """
    Id_azienda: int
    Id_credenziali: int
    Tipo: str
    Nome: str
    Indirizzo: str
    Co2_consumata: Optional[float] = None
    Co2_compensata: Optional[float] = None
    Token : int = 0
    data : datetime = None


