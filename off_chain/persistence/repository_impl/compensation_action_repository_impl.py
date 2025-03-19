import datetime
from abc import ABC
from configuration.db_manager_setting import DatabaseManagerSetting
from configuration.log_load_setting import logger
from domain.repository.compensation_action_repository import CompensationActionRepository


class CompensationActionRepositoryImpl(CompensationActionRepository, ABC):
    # Class variable that stores the single instance
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(CompensationActionRepositoryImpl, cls).__new__(cls)
            cls._instance.db_manager_setting = DatabaseManagerSetting()
            logger.info("BackEnd: Successfully initializing the instance for CompensationActionRepositoryImpl.")
        return cls._instance

    def get_lista_azioni(self, id_azienda: int) -> list:
        query = """
        SELECT * FROM Azioni_compensative WHERE Id_azienda = ?;
        """
        return self.db_manager_setting.fetch_query(query, (id_azienda,))

    def get_lista_azioni_per_data(self, id_azienda: int, data_start: datetime, data_end: datetime) -> list:
        query = """
        SELECT * FROM Azioni_compensative
        WHERE Id_azienda = ? AND Data BETWEEN ? AND ?;
        """
        return self.db_manager_setting.fetch_query(query, (id_azienda, data_start, data_end))

    def get_lista_azioni_ordinata(self, id_azienda: int) -> list:
        query = """
        SELECT * FROM Azioni_compensative
        WHERE Id_azienda = ?
        ORDER BY Co2_compensata DESC;
        """
        return self.db_manager_setting.fetch_query(query, (id_azienda,))

    def get_co2_compensata(self, id_azienda: int) -> float:
        query = """
        SELECT SUM(Co2_compensata) FROM Azioni_compensative WHERE Id_azienda = ?;
        """
        return self.db_manager_setting.fetch_query(query, (id_azienda,))[0][0]

    def inserisci_azione(self, data: datetime, azienda: int, co2_compensata: str, nome_azione: str):
        query = """
        INSERT INTO Azioni_compensative (Data, Id_azienda, Co2_compensata, Nome_azione)
        VALUES (?, ?, ?, ?);
        """
        return self.db_manager_setting.execute_query(query, (data, azienda, co2_compensata, nome_azione))
