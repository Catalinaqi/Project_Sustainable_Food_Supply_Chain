import datetime
from abc import ABC
from configuration.database import Database
from configuration.log_load_setting import logger
from domain.repository.compensation_action_repository import CompensationActionRepository
from persistence.query_builder import QueryBuilder
from model.compensation_action_model import CompensationActionModel


class CompensationActionRepositoryImpl( ABC):
    # Class variable that stores the single instance
    def __init__(self):
        super().__init__()
        self.db = Database()
        self.query_builder = QueryBuilder()




    def get_lista_azioni(self, id_azienda: int,  data_start: datetime = None, data_end: datetime = None, ordinamento: str = None) -> list[CompensationActionModel]:

        self.query_builder.select("Id_azione","Id_azienda","Data","Co2_compensata","Nome_azione").table("Azioni_compensative").where("Id_azienda", "=", id_azienda)

        if data_start and data_end:
            self.query_builder.where("Data", ">", data_start).where("Data", "<", data_end)
            
        if ordinamento:
            self.query_builder.order_by("Co2_compensata", "DESC")

        query,value = (
            self.query_builder.get_query()
        )
        results = self.db.fetch_results(query, value)
        lista_op= [
                CompensationActionModel(
                    Id_azione=row[0],
                    Id_azienda=row[1],
                    Data_azione=row[2],
                    Co2_compensata=row[3],
                    Nome_azione=row[4],               
            )
            for row in results
            ]

        return lista_op
    







    def get_co2_compensata(self, id_azienda: int) -> float:
        query,value = (
            self.query_builder
                .select("SUM(Co2_compensata)")
                .table("Azioni_compensative")
                .where("Id_azienda", "=", id_azienda)
        )
        try:
            return float(self.db.fetch_one(query, value))
        except:
            raise ValueError

    def inserisci_azione(self, data: datetime, azienda: int, co2_compensata: str, nome_azione: str):
        query = """
        INSERT INTO Azioni_compensative (Data, Id_azienda, Co2_compensata, Nome_azione)
        VALUES (?, ?, ?, ?);
        """
        #TODO
        return self.db.execute_query(query, (data, azienda, co2_compensata, nome_azione))
