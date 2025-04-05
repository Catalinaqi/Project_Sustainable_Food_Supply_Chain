from abc import ABC
from configuration.database import Database
from configuration.log_load_setting import logger
from domain.repository.composition_repository import CompositionRepository
from persistence.query_builder import QueryBuilder


class CompositionRepositoryImpl(CompositionRepository, ABC):
    
    def __init__(self):
        super().__init__()
        self.db = Database()
        self.query_builder = QueryBuilder()


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
        return self.db_manager_setting.fetch_results(query, (azienda,))
