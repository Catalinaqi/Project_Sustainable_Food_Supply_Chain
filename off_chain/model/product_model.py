from dataclasses import dataclass


@dataclass
class ProductModel:
    """
    Data model for transporting product information between layers.
    """
    Id_prodotto: int
    Nome_prodotto: str
    Quantita_prodotto: float
    Stato_prodotto: int
    Nome_azienda: str

    def save(self):
        pass

    @classmethod
    def see_all_products(cls):
        pass
