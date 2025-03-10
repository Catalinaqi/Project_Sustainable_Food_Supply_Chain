import datetime
from abc import ABC, abstractmethod


class CertificationRepository(ABC):
    """
    Repository interface for certificazione persistence.
    """

    @abstractmethod
    def get_certificazione_by_prodotto(self, prodotto: int) -> list:
        """Restituisce la certificazione del prodotto selezionato."""
        pass

    @abstractmethod
    def get_numero_certificazioni(self, id_azienda: int) -> int:
        """Restituisce il numero di certificazioni di un'azienda."""
        pass

    @abstractmethod
    def is_certificato(self, id_prodotto: int) -> bool:
        """Restituisce true se il prodotto è certificato, false altrimenti."""
        pass

    @abstractmethod
    def inserisci_certificato(self, prodotto: int, tipo: str, azienda: int, data: datetime):
        """Inserisce un nuovo certificato."""
        pass
