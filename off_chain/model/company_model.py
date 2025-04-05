from dataclasses import dataclass
from typing import Optional

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
    Co2_consumata: Optional[int] = None
    Co2_compensata: Optional[int] = None
