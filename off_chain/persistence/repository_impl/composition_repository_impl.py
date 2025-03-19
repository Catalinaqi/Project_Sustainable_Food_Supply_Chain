from abc import ABC
from configuration.db_manager_setting import DatabaseManagerSetting
from configuration.log_load_setting import logger
from domain.repository.composition_repository import CompositionRepository


class CompositionRepositoryImpl(CompositionRepository, ABC):
    # Class variable that stores the single instance
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(CompositionRepositoryImpl, cls).__new__(cls)
            cls._instance.db_manager_setting = DatabaseManagerSetting()
            logger.info("BackEnd: Successfully initializing the instance for CompositionRepositoryImpl.")
        return cls._instance

    def get_prodotti_to_composizione(self, azienda: int) -> list:
        query = """
        SELECT Id_prodotto, Nome, Quantita
        FROM Prodotto
        WHERE Stato != 110
        AND Id_prodotto IN (
            SELECT Id_prodotto
            FROM Operazione
            WHERE Id_azienda = ? AND Operazione = "Trasformazione"
        )
        """
        return self.db_manager_setting.fetch_query(query, (azienda,))
