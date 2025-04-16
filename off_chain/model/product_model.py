from dataclasses import dataclass, field
from model.componente_model import Componente

@dataclass
class ProductModel:
    """
    Data model for transporting product information between layers.
    """
    Id_prodotto: int
    Nome_prodotto: str
    
    """Quantita_prodotto: float
    Stato_prodotto: int
    Nome_azienda: str"""

    componenti: list[Componente] = field(default_factory=list)

    def save(self):
        pass

    @classmethod
    def see_all_products(cls):
        pass
