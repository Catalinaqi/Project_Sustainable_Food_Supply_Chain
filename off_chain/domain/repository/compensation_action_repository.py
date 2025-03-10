import datetime
from abc import ABC, abstractmethod


class CompensationActionRepository(ABC):
    """
    Repository interface for Azioni_compensative persistence.
    """

    @abstractmethod
    def get_lista_azioni(self, id_azienda: int) -> list:
        """Restituisce la lista delle azioni compensative per azienda."""
        pass

    @abstractmethod
    def get_lista_azioni_per_data(self, id_azienda: int, data_start: datetime, data_end: datetime) -> list:
        """Restituisce la lista di azioni compensative filtrate per data."""
        pass

    @abstractmethod
    def get_lista_azioni_ordinata(self, id_azienda: int) -> list:
        """Restituisce la lista di azioni compensative ordinata per co2 risparmiata."""
        pass

    @abstractmethod
    def get_co2_compensata(self, id_azienda: int) -> float:
        """Restituisce il valore della co2 compensata per azienda."""
        pass

    #

    @abstractmethod
    def inserisci_azione(self, data: datetime, azienda: int, co2_compensata: str, nome_azione: str):
        """Inserisce una nuova azione compensativa."""
        pass
