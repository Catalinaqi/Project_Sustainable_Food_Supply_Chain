from dataclasses import dataclass, field

@dataclass
class ProductStandardModel:
    """
    Data model for transporting product information between layers.
    """
    id_prodotto: int
    nome_prodotto: str