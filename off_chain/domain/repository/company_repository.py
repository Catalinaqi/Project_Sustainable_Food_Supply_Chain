from abc import ABC, abstractmethod
from model.company_model import CompanyModel


class CompanyRepository(ABC):
    """
    Repository interface for aziende persistence.
    """


    @abstractmethod
    def get_lista_aziende(self) -> list:
        """Restituisce la lista di tutte le aziende con i rispettivi valori di CO2 consumata e compensata."""
        pass


    @abstractmethod
    def get_azienda(self, n):
        """Get..."""
        pass
