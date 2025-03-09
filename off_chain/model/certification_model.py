import datetime
from dataclasses import dataclass


@dataclass
class CertificationModel:
    """
    Data model for transporting product information between layers.
    """
    Id_certificato: int
    Nome_prodotto: str
    Descrizione_certificato: str
    Nome_azienda: str
    Data_certificato: datetime
