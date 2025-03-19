from abc import ABC, abstractmethod
from model.company_model import CompanyModel


class CompanyRepository(ABC):
    """
    Repository interface for aziende persistence.
    """

    @abstractmethod
    def get_lista_rivenditori(self) -> list:
        """Restituisce la lista dei rivenditori."""
        pass

    @abstractmethod
    def get_lista_aziende(self) -> list:
        """Restituisce la lista di tutte le aziende con i rispettivi valori di CO2 consumata e compensata."""
        pass

    @abstractmethod
    def get_lista_aziende_ordinata(self) -> list:
        """Restituisce la lista ordinata per saldo CO2 di tutte le aziende."""
        pass

    @abstractmethod
    def get_lista_aziende_filtrata_tipo(self, tipo: str) -> list:
        """
        Restituisce la lista di tutte le aziende con i rispettivi valori di CO2 consumata e compensata
        filtrata per tipo
        """
        pass

    @abstractmethod
    def get_azienda_by_nome(self, nome: str) -> list:
        """
        Restituisce la lista di tutte le aziende con i rispettivi valori di CO2 consumata e compensata
        filtrata per nome
        """
        pass

    @abstractmethod
    def get_azienda_by_id(self, id_: int) -> list:
        """Get..."""
        pass

    @abstractmethod
    def get_azienda(self, n):
        """Get..."""
        pass
