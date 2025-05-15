from dataclasses import dataclass


@dataclass
class ThresholdModel:
    """
    Represents operation thresholds for products.
    """
    prodotto: str
    soglia_massima: float
    tipo: str
    
