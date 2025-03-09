from dataclasses import dataclass


@dataclass
class ThresholdModel:
    """
    Represents operation thresholds for products.
    """
    Operazione: str
    Prodotto: str
    Soglia_Massima: float
    Tipo: str
