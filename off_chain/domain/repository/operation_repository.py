import datetime
from abc import ABC, abstractmethod
from model.operation_model import OperationModel


class OperationRepository(ABC):
    """
    Repository interface for Operazione persistence.
    """

    @abstractmethod
    def get_operazioni_ordinate_co2(self, azienda: int) -> list:
        """Restituisce la lista di tutte le operazioni effettuate da una certa azienda ordinate per co2 consumata """
        pass

    @abstractmethod
    def get_operazioni_by_data(self, azienda: int, d1: datetime, d2: datetime) -> list:
        """Restituisce la lista di tutte le operazioni effettuate da una certa azienda ordinate per co2 consumata """
        pass

    @abstractmethod
    def get_operazioni_by_azienda(self, azienda: int) -> list:
        """Restituisce la lista di tutte le operazioni effettuate da una certa azienda """
        pass

    @abstractmethod
    def inserisci_operazione_azienda_rivenditore(self, azienda: int, prodotto: [int], data: datetime, co2: float,
                                                 evento: str):
        """..."""
        pass

    @abstractmethod
    def inserisci_operazione_azienda_trasformazione(self,azienda: int, prodotto: int, data: datetime, co2: float,
                                                    evento: str, quantita: int = 0,
                                                    materie_prime: str = None):
        """..."""
        pass

    @abstractmethod
    def inserisci_operazione_azienda_trasporto(self,azienda: int, prodotto: int, data: datetime, co2: float,
                                               evento: str, nuovo_stato: int):
        """..."""
        pass

    @abstractmethod
    def inserisci_operazione_azienda_agricola(self,nome: str, quantita: int, azienda: int, data: datetime, co2: float,
                                              evento: str):
        """
        Le seguenti quattro funzioni permettono l'inserimento di un'operazione
        a seconda del tipo di azienda che la sta effettuando
        """
        pass
