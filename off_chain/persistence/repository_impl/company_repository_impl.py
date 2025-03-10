from abc import ABC
from off_chain.configuration.db_manager_setting import DatabaseManagerSetting
from off_chain.configuration.log_load_setting import logger
from off_chain.domain.repository.company_repository import CompanyRepository
from off_chain.model.company_model import CompanyModel


class CompanyRepositoryImpl(CompanyRepository, ABC):
    """
     Implementing the aziende repository.
     """

    # Class variable that stores the single instance
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(CompanyRepositoryImpl, cls).__new__(cls)
            cls._instance.db_manager_setting = DatabaseManagerSetting()
            logger.info("BackEnd: Successfully initializing the instance for CompanyRepositoryImpl.")
        return cls._instance

    def get_lista_rivenditori(self) -> list:
        query = """
        SELECT Id_azienda, Tipo, Indirizzo, Nome 
        FROM Azienda WHERE Tipo = "Rivenditore"
        """
        return self.db_manager_setting.fetch_query(query)

    def get_lista_aziende(self) -> list:
        query = """
        SELECT Id_azienda, Tipo, Indirizzo, Nome 
        FROM Azienda WHERE Tipo != "Certificatore"
        """
        aziende = self.db_manager_setting.fetch_query(query)
        lista_con_co2 = []
        for azienda in aziende:
            query_co2_consumata = """
            SELECT SUM(Consumo_CO2) FROM Operazione WHERE Id_azienda = ?;
            """
            query_co2_compensata = """
            SELECT SUM(Co2_compensata) FROM Azioni_compensative WHERE Id_azienda = ?;
            """
            if not self.db_manager_setting.fetch_query(query_co2_consumata, (azienda[0],))[0][0]:
                co2_consumata = 0
            else:
                co2_consumata = self.db_manager_setting.fetch_query(query_co2_consumata, (azienda[0],))[0][0]
            if not self.db_manager_setting.fetch_query(query_co2_compensata, (azienda[0],))[0][0]:
                co2_compensata = 0
            else:
                co2_compensata = self.db_manager_setting.fetch_query(query_co2_compensata, (azienda[0],))[0][0]
            lista_con_co2.append((azienda, co2_consumata, co2_compensata))
        return lista_con_co2

    def get_lista_aziende_ordinata(self) -> list:
        lista_ordinata = sorted(self.get_lista_aziende(), key=lambda x: (x[2] or 0) - (x[1] or 0),
                                reverse=True)
        return lista_ordinata

    def get_lista_aziende_filtrata_tipo(self, tipo: str) -> list:
        query = """
        SELECT Id_azienda, Tipo, Indirizzo, Nome 
        FROM Azienda WHERE Tipo != "Certificatore"
        AND Tipo = ?
        """
        aziende = self.db_manager_setting.fetch_query(query, (tipo,))
        lista_con_co2 = []
        for azienda in aziende:
            query_co2_consumata = """
            SELECT SUM(Consumo_CO2) FROM Operazione WHERE Id_azienda = ?;
            """
            query_co2_compensata = """
            SELECT SUM(Co2_compensata) FROM Azioni_compensative WHERE Id_azienda = ?;
            """
            if not self.db_manager_setting.fetch_query(query_co2_consumata, (azienda[0],))[0][0]:
                co2_consumata = 0
            else:
                co2_consumata = self.db_manager_setting.fetch_query(query_co2_consumata, (azienda[0],))[0][0]
            if not self.db_manager_setting.fetch_query(query_co2_compensata, (azienda[0],))[0][0]:
                co2_compensata = 0
            else:
                co2_compensata = self.db_manager_setting.fetch_query(query_co2_compensata, (azienda[0],))[0][0]
            lista_con_co2.append((azienda, co2_consumata, co2_compensata))
        return lista_con_co2

    def get_azienda_by_nome(self, nome: str) -> list:
        query = """
        SELECT Id_azienda, Tipo, Indirizzo, Nome 
        FROM Azienda WHERE Tipo != "Certificatore"
        AND Nome = ?
        """
        aziende = self.db_manager_setting.fetch_query(query, (nome,))
        lista_con_co2 = []
        for azienda in aziende:
            query_co2_consumata = """
            SELECT SUM(Consumo_CO2) FROM Operazione WHERE Id_azienda = ?;
            """
            query_co2_compensata = """
            SELECT SUM(Co2_compensata) FROM Azioni_compensative WHERE Id_azienda = ?;
            """
            if not self.db_manager_setting.fetch_query(query_co2_consumata, (azienda[0],))[0][0]:
                co2_consumata = 0
            else:
                co2_consumata = self.db_manager_setting.fetch_query(query_co2_consumata, (azienda[0],))[0][0]
            if not self.db_manager_setting.fetch_query(query_co2_compensata, (azienda[0],))[0][0]:
                co2_compensata = 0
            else:
                co2_compensata = self.db_manager_setting.fetch_query(query_co2_compensata, (azienda[0],))[0][0]
            lista_con_co2.append((azienda, co2_consumata, co2_compensata))
        return lista_con_co2

    def get_azienda_by_id(self, id_: int) -> list:
        query = """
        SELECT Id_azienda, Tipo, Indirizzo, Nome FROM Azienda WHERE Id_azienda = ?;
        """
        aziende = self.db_manager_setting.fetch_query(query, (id_,))
        lista_con_co2 = []
        for azienda in aziende:
            query_co2_consumata = """
            SELECT SUM(Consumo_CO2) FROM Operazione WHERE Id_azienda = ?;
            """
            query_co2_compensata = """
            SELECT SUM(Co2_compensata) FROM Azioni_compensative WHERE Id_azienda = ?;
            """
            if not self.db_manager_setting.fetch_query(query_co2_consumata, (azienda[0],))[0][0]:
                co2_consumata = 0
            else:
                co2_consumata = self.db_manager_setting.fetch_query(query_co2_consumata, (azienda[0],))[0][0]
            if not self.db_manager_setting.fetch_query(query_co2_compensata, (azienda[0],))[0][0]:
                co2_compensata = 0
            else:
                co2_compensata = self.db_manager_setting.fetch_query(query_co2_compensata, (azienda[0],))[0][0]
            lista_con_co2.append((azienda, co2_consumata, co2_compensata))
        return lista_con_co2

    def get_azienda(self, n):
        return self.get_lista_aziende()[n]
