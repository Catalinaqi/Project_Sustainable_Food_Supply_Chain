from abc import ABC, abstractmethod


class ProductRepository(ABC):
    """
    Repository interface for product persistence.
    """

    @abstractmethod
    def get_storico_prodotto(self, prodotto: int) -> list:
        """Restituisce lo storico del prodotto selezionato."""
        pass

    @abstractmethod
    def co2_consumata_prodotti(self, prodotti: [int]) -> list:
        """..."""
        pass

    @abstractmethod
    def get_lista_prodotti(self) -> list:
        """Restituisce la lista di prodotti sugli scaffali per il guest."""
        pass

    @abstractmethod
    def get_prodotti_ordinati_co2(self) -> list:
        """Restituisce tutti i prodotti sugli scaffali ordinati per co2 consumata."""
        pass

    @abstractmethod
    def get_prodotti_by_nome(self, nome: str) -> list:
        """Restituisce tutti i prodotti sugli scaffali con un certo nome."""
        pass

    @abstractmethod
    def get_lista_prodotti_by_rivenditore(self, rivenditore: int) -> list:
        """Restituisce una lista di prodotti sullo scaffale filtrati per rivenditore."""
        pass

    @abstractmethod
    def get_prodotti_certificati(self) -> list:
        """Restituisce la lista di tutti i prodotti sullo scaffale certificati."""
        pass

    @abstractmethod
    def get_prodotti_certificati_by_rivenditore(self, id_rivenditore: int) -> list:
        """Restituisce i prodotti certificati sullo scaffale filtrati per rivenditore."""
        pass

    @abstractmethod
    def get_prodotti_certificati_ordinati_co2(self) -> list:
        """Restituisce i prodotti certificati sullo scaffale ordinati per co2 consumata."""
        pass

    @abstractmethod
    def get_prodotti_certificati_by_nome(self, nome: str) -> list:
        """Restituisce i prodotti certificati sullo scaffale filtrati per nome."""
        pass

    @abstractmethod
    def get_prodotti_to_rivenditore(self) -> list:
        """Get ."""
        pass

    @abstractmethod
    def get_materie_prime(self, azienda: int) -> list:
        """
        Questa funzione restituisce i prodotti che l'azienda di trasformazione
        può inserire nella tabella "composizione" come valori dell'attributo "materia prima"
        """
        pass
