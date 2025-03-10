import datetime
from dataclasses import dataclass


@dataclass
class CompensationActionModel:
    """
    Model for CompensationActionModel.
    """
    Id_azione: int = None
    Data_azione: datetime = None
    Id_azienda: int = None
    Co2_compensata: float = None
    Nome_azione: str = None


