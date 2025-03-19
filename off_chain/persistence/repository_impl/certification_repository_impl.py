import datetime
from abc import ABC
from configuration.db_manager_setting import DatabaseManagerSetting
from configuration.log_load_setting import logger
from domain.repository.certification_repository import CertificationRepository


class CertificationRepositoryImpl(CertificationRepository, ABC):
    """
     Implementing the certificato repository.
     """

    # Class variable that stores the single instance
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(CertificationRepositoryImpl, cls).__new__(cls)
            cls._instance.db_manager_setting = DatabaseManagerSetting()
            logger.info("BackEnd: Successfully initializing the instance for CertificationRepositoryImpl.")
        return cls._instance

    def get_certifications_by_product_interface(self, prodotto: int) -> list:
        query = """
        SELECT 
            Certificato.Id_certificato,
            Prodotto.Nome,
            Certificato.Descrizione,
            Azienda.Nome,
            Certificato.Data
        FROM Certificato
        JOIN Azienda ON Certificato.Id_azienda_certificatore = Azienda.Id_azienda
        JOIN Prodotto ON Certificato.Id_prodotto = Prodotto.Id_prodotto
        WHERE Certificato.Id_prodotto = ?;
        """
        return self.db_manager_setting.fetch_query(query, (prodotto,))

    def get_numero_certificazioni(self, id_azienda: int) -> int:
        query = """
        SELECT COUNT(*) FROM Certificato WHERE Id_azienda_certificatore = ?;
        """
        return self.db_manager_setting.fetch_query(query, (id_azienda,))[0]

    def is_certificato(self, id_prodotto: int) -> bool:
        query = """
        SELECT * FROM Certificato WHERE Id_prodotto = ?;
        """
        if not self.db_manager_setting.fetch_query(query, (id_prodotto,)):
            return False
        return True

    def inserisci_certificato(self, prodotto: int, tipo: str, azienda: int, data: datetime):
        query = """
        INSERT INTO Certificato (Id_prodotto, Descrizione, Id_azienda_certificatore, Data)
        VALUES (?, ?, ?, ?);
        """
        self.db_manager_setting.execute_query(query, (prodotto, tipo, azienda, data))
    # Restituisce la certificazione del prodotto selezionato
    def get_certificazione_by_prodotto(self, prodotto):
        query = """
        SELECT 
            Certificato.Id_certificato,
            Prodotto.Nome,
            Certificato.Descrizione,
            Azienda.Nome,
            Certificato.Data
        FROM Certificato
        JOIN Azienda ON Certificato.Id_azienda_certificatore = Azienda.Id_azienda
        JOIN Prodotto ON Certificato.Id_prodotto = Prodotto.Id_prodotto
        WHERE Certificato.Id_prodotto = ?;
        """
        return self.db_manager_setting.execute_query(query, (prodotto,))