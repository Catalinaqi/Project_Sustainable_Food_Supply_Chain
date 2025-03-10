from abc import ABC, abstractmethod
from off_chain.model.product_model import ProductModel


class CompositionRepository(ABC):
    """
    Repository interface for Composizione persistence.
    """

    @abstractmethod
    def get_prodotti_to_composizione(self, azienda: int) -> list:
        """Restituisce i prodotti con cui un trasformatore può fare la composizione."""
        pass
