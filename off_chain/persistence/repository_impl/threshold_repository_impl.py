from abc import ABC

from configuration.database import Database
from configuration.log_load_setting import logger
from domain.repository.threshold_repository import ThresholdRepository
from model.threshold_model import ThresholdModel
from persistence.query_builder import QueryBuilder
from persistence.repository_impl import db_default_string


class ThresholdRepositoryImpl(ABC):
    # Class variable that stores the single instance

    def __init__(self):
        super().__init__()
        self.db = Database()
        self.query_builder = QueryBuilder()
   

    def get_lista_soglie(self, tipo_azienda : str) -> list[ThresholdModel]:
            self.query_builder.select("*").table("Soglie")


            #TODO aggiungere stringhe giuste
            if tipo_azienda == db_default_string.TIPO_AZIENDA_AGRICOLA:
                self.query_builder.where("Operazione", "=", db_default_string.TIPO_OP_PRODUZIONE)
                self.query_builder.where("Tipo", "=", "materia prima")
            elif tipo_azienda == db_default_string.TIPO_AZIENDA_TRASFORMATORE:
                self.query_builder.where("Tipo", "=", "prodotto finale")
            elif tipo_azienda == db_default_string.TIPO_AZIENDA_TRASPORTATORE:
                self.query_builder.where("Tipo", "=", "trasporto")
            else:
                logger.error("Tipo di azienda non valido") 
                
            query, value = (self.query_builder.get_query() )

            try:
            
                return [ThresholdModel(*x) for x in self.db.fetch_results(query, value)]
        
            except Exception as e:
               logger.error(f"Errore durante il recupero delle soglie: {e}")
            return []
        
