from abc import ABC, abstractmethod


class ThresholdRepository(ABC):
    """
    Repository interface for Soglie persistence.
    """

    @abstractmethod
    def get_lista_soglie(self) -> list:
        """Restituisce la lista di tutte le soglie."""
        pass

    @abstractmethod
    def get_prodotti_to_azienda_agricola(self) -> list:
        """
        Le seguenti quattro funzioni restituiscono gli elementi che verranno visualizzati nelle
        rispettive combo box, a seconda del tipo di azienda che sta effettuando l'operazione
        """
        pass

    @abstractmethod
    def get_prodotti_to_azienda_trasporto(self, destinatario: str) -> list:
        """..."""
        pass

    @abstractmethod
    def get_prodotti_to_azienda_trasformazione(self, id_operation: int) -> list:
        """..."""
        pass

    @abstractmethod
    def get_soglia_by_operazione_and_prodotto(self, operazione: str, prodotto: str) -> int:
        """Questa funzione restituisce la soglia data l'operazione e il prodotto"""
        pass
