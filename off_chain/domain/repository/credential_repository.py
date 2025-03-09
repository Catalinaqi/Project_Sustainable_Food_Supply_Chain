from abc import ABC, abstractmethod


class CredentialRepository(ABC):

    @abstractmethod
    def get_lista_credenziali(self) -> list:
        pass

    @abstractmethod
    def get_azienda_by_id(self, id_: int) -> list:
        pass

    @abstractmethod
    def inserisci_credenziali_e_azienda(self, username, password, tipo, indirizzo, secret_key):
        pass
